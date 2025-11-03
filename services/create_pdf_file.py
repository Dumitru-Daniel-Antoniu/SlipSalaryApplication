import logging
import os
import pikepdf
import uuid

from datetime import datetime

from db.models.employees_cnp_model import EmployeesCNP
from db.models.employees_name_model import EmployeesName
from db.models.employees_personal_information_model import EmployeesPersonalInformation
from db.models.employees_salary_model import EmployeesSalary
from db.session import async_session

from flask import abort

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, OperationalError, SQLAlchemyError

from werkzeug.exceptions import HTTPException


logging.basicConfig(level=logging.INFO)


async def generate_pdf_data(manager_id: int, employee_id: int) -> str:
    if not isinstance(manager_id, int) or not isinstance(employee_id, int):
        abort(400, "Employee ID and manager ID must be integers")

    async with async_session() as session:
        try:
            cnp_manager_data = await session.get(EmployeesCNP, manager_id)
            if cnp_manager_data is None:
                abort(404, "Manager not found")

            personal_manager_data = await session.execute(
                select(EmployeesPersonalInformation).where(
                    EmployeesPersonalInformation.employee_id == cnp_manager_data.cnp
                )
            )

            personal_manager = personal_manager_data.scalar_one_or_none()
            if not personal_manager:
                abort(404, "Personal information for the manager not found")
            if personal_manager.position != "Manager":
                abort(403, "Only managers can generate a PDF file")

            department_manager = personal_manager.department

            cnp_employee_data = await session.get(EmployeesCNP, employee_id)
            if cnp_employee_data is None:
                abort(404, "Employee not found")

            personal_employee_data = await session.execute(
                select(EmployeesPersonalInformation).where(
                    EmployeesPersonalInformation.employee_id == cnp_employee_data.cnp
                )
            )

            personal_employee = personal_employee_data.scalar_one_or_none()
            if not personal_employee:
                abort(404, "Personal information for the employee not found")

            department_employee = personal_employee.department

            logging.info("The department of the manager is %s", department_manager)
            logging.info("The department of the employee is %s", department_employee)
            if department_manager != department_employee:
                logging.info("Correct error")
                abort(403, "Managers can only generate PDF files for employees in their own department")

            logging.info("Keep going...")
            now = datetime.now()
            month = now.month
            year = now.year

            statement = (
                select(
                    EmployeesCNP.id,
                    EmployeesCNP.cnp,
                    EmployeesName.name,
                    EmployeesName.surname,
                    EmployeesPersonalInformation.position,
                    EmployeesPersonalInformation.department,
                    EmployeesSalary.salary,
                    EmployeesSalary.bonus
                )
                .select_from(EmployeesCNP)
                .join(EmployeesName, EmployeesName.employee_id == EmployeesCNP.cnp)
                .join(EmployeesPersonalInformation, EmployeesPersonalInformation.employee_id == EmployeesCNP.cnp)
                .join(EmployeesSalary, EmployeesSalary.employee_id == EmployeesCNP.cnp)
                .where(
                    EmployeesCNP.id == employee_id,
                    EmployeesSalary.month == month,
                    EmployeesSalary.year == year
                )
            )

            result = await session.execute(statement)

            rows = result.fetchall()
            if len(rows) != 1:
                abort(500, "The query did not return exactly one employee record")

            row = rows[0]

            filename = f"Employee_monthly_salary_{row[2]}_{row[3]}_{month}_{year}_{uuid.uuid4().hex}.pdf"
            filepath = os.path.join("temporary/pdf", filename)
            temppath = os.path.join("temporary/pdf", f"{filename}_temp.pdf")

            doc = SimpleDocTemplate(temppath, pagesize=A4)
            styles = getSampleStyleSheet()
            title = ParagraphStyle(
                f'{row[2]} {row[3]} salary report',
                parent=styles['Title'],
                fontSize=24,
                textColor=colors.HexColor("#2E86C1"),
                alignment=1,
                spaceAfter=20
            )
            info = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor("#212F3C"),
                spaceAfter=10
            )

            elements = [
                Paragraph("Monthly Salary Statement", title),
                Spacer(1, 12),
                Paragraph(f"<b>Employee ID:</b> {row[0]}", info),
                Paragraph(f"<b>Name:</b> {row[2]}", info),
                Paragraph(f"<b>Surname:</b> {row[3]}", info),
                Paragraph(f"<b>CNP:</b> {row[1]}", info),
                Paragraph(f"<b>Position:</b> {row[4]}", info),
                Paragraph(f"<b>Department:</b> {row[5]}", info),
                Spacer(1, 20),
            ]

            data = [
                ["Month", "Year", "Salary", "Bonus", "Total"],
                [month, year, f"{row[6]:.2f} RON", f"{row[7]:.2f} RON", f"{row[6] + row[7]:.2f} RON"]
            ]

            table = Table(data, hAlign='CENTER')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#AED6F1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1B4F72")),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#EAF2F8")),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#1B4F72")),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 30))

            doc.build(elements)

            with pikepdf.open(temppath) as file:
                file.save(filepath, encryption=pikepdf.Encryption(owner=str(row[1]), user=str(row[1]), allow=pikepdf.Permissions(extract=False, print_highres=True, print_lowres=True)))
            os.remove(temppath)

            return filepath
        except OperationalError:
            abort(500, "Database connection error or deadlock")
        except SQLAlchemyError:
            abort(500, "General database error")
        except MultipleResultsFound:
            abort(500, "Multiple records of personal information for an employee")
        except pikepdf.PasswordError:
            abort(500, "Error in PDF encryption process")
        except pikepdf.PdfError:
            abort(500, "Error in PDF processing")
        except HTTPException as e:
            raise e
        except Exception:
            abort(500, "Unexpected error")

from pydantic import BaseModel, Field, StrictStr


class EmployeesEmailSchema(BaseModel):
    email: StrictStr
    employee_id: StrictStr = Field(alias="employeeId")

    class Config:
        from_attributes = True
        populate_by_name = True

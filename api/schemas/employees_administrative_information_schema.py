from pydantic import BaseModel, Field, StrictInt

class EmployeesAdministrativeInformationSchema(BaseModel):
    month_id: StrictInt = Field(alias="monthId")
    employee_id: StrictInt = Field(alias="employeeId")

    class Config:
        from_attributes = True
        populate_by_name = True

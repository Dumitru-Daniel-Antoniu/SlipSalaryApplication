from pydantic import BaseModel, Field, StrictInt, StrictStr, field_validator
from datetime import date

BIRTH_MIN = date(1965, 1, 1)
BIRTH_MAX = date(2006, 12, 31)

class EmployeesPersonalInformationSchema(BaseModel):
    position: StrictStr
    department: StrictStr
    date_of_birth: date = Field(alias="dateOfBirth")
    date_of_hire: date = Field(alias="dateOfHire")
    employee_id: StrictInt = Field(alias="employeeId")

    @field_validator("date_of_birth")
    def date_of_birth_validator(cls, v: date) -> date:
        if not (BIRTH_MIN <= v <= BIRTH_MAX):
            raise ValueError("Date of birth must be between 1965-01-01 and 2006-12-31")
        return v

    @field_validator("date_of_hire")
    def date_of_hire_validator(cls, v: date, info):
        dob = info.data.get("date_of_birth")
        if dob and v <= dob:
            raise ValueError("Date of hire must be after the date of birth")
        if v > date.today():
            raise ValueError("Date of hire cannot be in the future")
        return v

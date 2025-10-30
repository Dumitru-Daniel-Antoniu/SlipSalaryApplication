from pydantic import BaseModel, Field, StrictInt, StrictStr, field_validator

class EmployeesNameSchema(BaseModel):
    name: StrictStr
    surname: StrictStr
    employee_id: StrictInt = Field(alias="employeeId")


    @field_validator("name", "surname")
    def name_and_surname_validator(cls, v: str) -> str:
        if not all(ch.isalpha() or ch.isspace() for ch in v) or v.strip() == "":
            raise ValueError("Name and surname must contain only alphabetic characters and spaces")
        return v

    class Config:
        from_attributes = True
        populate_by_name = True

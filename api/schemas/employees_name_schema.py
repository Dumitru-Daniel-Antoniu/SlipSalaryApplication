from pydantic import BaseModel, StrictStr, field_validator

class EmployeesNameSchema(BaseModel):
    cnp: StrictStr
    name: StrictStr
    surname: StrictStr

    @field_validator("cnp")
    def cnp_validator(cls, v: str) -> str:
        if not (len(v) == 13 and v.isdigit()):
            raise ValueError("CNP must have exactly 13 digits")
        return v

    @field_validator("name", "surname")
    def name_and_surname_validator(cls, v: str) -> str:
        if not all(ch.isalpha() or ch.isspace() for ch in v) or v.strip() == "":
            raise ValueError("Name and surname must contain only alphabetic characters and spaces")
        return v

    class Config:
        from_attributes = True
        populate_by_name = True

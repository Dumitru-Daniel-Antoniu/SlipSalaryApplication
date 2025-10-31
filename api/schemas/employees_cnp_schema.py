from pydantic import BaseModel, StrictInt, StrictStr, field_validator

class EmployeesCNPSchema(BaseModel):
    cnp: StrictStr


    @field_validator("cnp")
    def cnp_validator(cls, v: str) -> str:
        if not (len(v) == 13 and v.isdigit()):
            raise ValueError("CNP must have exactly 13 digits")
        return v

    class Config:
        from_attributes = True
        populate_by_name = True

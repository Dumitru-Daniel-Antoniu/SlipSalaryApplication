from pydantic import BaseModel, Field, StrictFloat, StrictInt

class EmployeesSalarySchema(BaseModel):
    month: StrictInt = Field(ge=1, le=12)
    year: StrictInt = Field(ge=1965)
    salary: StrictFloat = Field(ge=4000, le=15000)
    bonus: StrictFloat = Field(ge=0, le=1000)
    month_id: StrictInt = Field(alias="monthId")

    class Config:
        from_attributes = True
        populate_by_name = True

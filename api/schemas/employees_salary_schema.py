from pydantic import BaseModel, Field, StrictFloat, StrictInt, StrictStr, model_validator

class EmployeesSalarySchema(BaseModel):
    month: StrictInt = Field(ge=1, le=12)
    year: StrictInt = Field(ge=1965)
    salary: StrictFloat = Field(ge=4000, le=15000)
    bonus: StrictFloat = Field(ge=0, le=1000)
    work: StrictInt
    vacation: StrictInt
    employee_id: StrictStr = Field(alias="employeeId")


    @model_validator(mode="after")
    def check_total_days(self):
        if self.work + self.vacation != 22:
            raise ValueError("Work and vacation days must be exactly 22")
        return self

    class Config:
        from_attributes = True
        populate_by_name = True

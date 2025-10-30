from pydantic import BaseModel, Field, StrictInt, model_validator

class EmployeesDaysSchema(BaseModel):
    work: StrictInt
    vacation: StrictInt
    month_id: StrictInt = Field(alias="monthId")

    @model_validator(mode="after")
    def check_total_days(self):
        if self.work + self.vacation != 22:
            raise ValueError("Work and vacation days must be exactly 22")
        return self

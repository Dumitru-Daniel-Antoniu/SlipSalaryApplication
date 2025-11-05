from datetime import datetime

from pydantic import BaseModel, Field, StrictInt, StrictStr


class IdempotencyKeySchema(BaseModel):
    key: StrictStr
    endpoint: StrictStr
    response_data: dict = Field(alias="responseData")
    status_code: StrictInt = Field(alias="statusCode")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True

from pydantic import BaseModel, HttpUrl

class ParseRequest(BaseModel):
    url: HttpUrl

class ParseResponse(BaseModel):
    message: str
    indicator_name: str
    monthly_rows_added: int
    yearly_rows_added: int
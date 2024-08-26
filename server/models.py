from pydantic import BaseModel


class URLRequest(BaseModel):
    url: str


class URLResponse(BaseModel):
    estimated_time: int
    task_id: str


class StatusResponse(BaseModel):
    status: str
    error: str = None


class TokenVerificationRequest(BaseModel):
    token: str

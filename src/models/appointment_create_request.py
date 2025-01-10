import datetime
from pydantic import BaseModel


class PracticeSetting(BaseModel):
    system: str
    code: str


class PostAppointmentRequest(BaseModel):
    specialty: list[PracticeSetting]
    start: datetime.datetime
    end: datetime.datetime
    service_request_id: str
    patient_id: str
    practitioner_id: str
    status: str = "pending"

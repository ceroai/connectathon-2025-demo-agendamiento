"""Modelo que representa el payload de la solicitud de aceptar o rechazar una cita."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Meta(BaseModel):
    profile: List[str] = [
        "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/BundleRespuesta"
    ]


class Identifier(BaseModel):
    value: str = "BundResp"


class Meta1(BaseModel):
    profile: List[str] = [
        "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/CitaRespuesta"
    ]


class Appointment(BaseModel):
    reference: str


class Actor(BaseModel):
    reference: str


class Text(BaseModel):
    status: str
    div: str


class ExtensionItem(BaseModel):
    url: str
    valueString: str


class CodingItem(BaseModel):
    system: str
    code: str


class SpecialtyItem(BaseModel):
    coding: List[CodingItem]


class BasedOnItem(BaseModel):
    reference: str


class Actor1(BaseModel):
    reference: str


class ParticipantItem(BaseModel):
    actor: Actor1
    required: str
    status: str


class Resource(BaseModel):
    resourceType: str
    meta: Meta1
    appointment: Optional[Appointment] = None
    actor: Optional[Actor] = None
    participantStatus: Optional[str] = None
    id: Optional[str] = None
    text: Optional[Text] = None
    extension: Optional[List[ExtensionItem]] = None
    status: Optional[str] = None
    specialty: Optional[List[SpecialtyItem]] = None
    start: Optional[str] = None
    end: Optional[str] = None
    basedOn: Optional[List[BasedOnItem]] = None
    participant: Optional[List[ParticipantItem]] = None


class Request(BaseModel):
    method: str = "PUT"
    url: str


class EntryItem(BaseModel):
    fullUrl: str
    resource: Resource
    request: Request


class AcceptRejectAppointment(BaseModel):
    resourceType: str = "Bundle"
    id: str = "BundResp"
    meta: Meta
    identifier: Identifier
    type: str = "transaction"
    timestamp: str = datetime.now().isoformat()
    entry: List[EntryItem]

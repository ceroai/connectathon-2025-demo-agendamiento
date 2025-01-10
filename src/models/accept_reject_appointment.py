"""Modelo que representa el payload de la solicitud de aceptar o rechazar una cita."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Meta(BaseModel):
    profile: List[str]


class Identifier(BaseModel):
    value: str


class Meta1(BaseModel):
    profile: List[str]


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
    method: str
    url: str


class EntryItem(BaseModel):
    fullUrl: str
    resource: Resource
    request: Request


class AcceptAppointment(BaseModel):
    resourceType: str
    id: str
    meta: Meta
    identifier: Identifier
    type: str
    timestamp: str
    entry: List[EntryItem]

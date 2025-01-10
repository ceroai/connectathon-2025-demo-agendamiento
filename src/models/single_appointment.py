from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Meta(BaseModel):
    versionId: str
    lastUpdated: str
    source: str
    profile: List[str]


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


class Actor(BaseModel):
    reference: str


class ParticipantItem(BaseModel):
    actor: Actor
    required: str
    status: str


class SingleAppointment(BaseModel):
    resourceType: str
    id: str
    meta: Meta
    extension: List[ExtensionItem]
    status: str
    specialty: List[SpecialtyItem]
    start: str
    end: str
    basedOn: List[BasedOnItem]
    participant: List[ParticipantItem]

"""Modelo que representa el resultado del get Appointments."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Meta(BaseModel):
    lastUpdated: str


class LinkItem(BaseModel):
    relation: str
    url: str


class Meta1(BaseModel):
    versionId: str
    lastUpdated: str
    source: str
    profile: List[str]


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


class Actor(BaseModel):
    reference: str


class ParticipantItem(BaseModel):
    actor: Actor
    required: str
    status: str


class Resource(BaseModel):
    resourceType: str
    id: str
    meta: Meta1
    text: Text
    extension: List[ExtensionItem]
    status: str
    specialty: List[SpecialtyItem]
    start: str
    end: str
    basedOn: List[BasedOnItem]
    participant: List[ParticipantItem]


class Search(BaseModel):
    mode: str


class EntryItem(BaseModel):
    fullUrl: str
    resource: Resource
    search: Search


class Appointment(BaseModel):
    resourceType: str
    id: str
    meta: Meta
    type: str
    total: int | None = None
    link: List[LinkItem]
    entry: List[EntryItem]

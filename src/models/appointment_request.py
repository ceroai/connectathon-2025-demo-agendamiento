"""Modelo que representa el payload de la solicitud de cita."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class LinkItem(BaseModel):
    relation: str
    url: str


class Text(BaseModel):
    status: str
    div: str


class CodingItem(BaseModel):
    system: str
    code: str
    display: str


class Details(BaseModel):
    coding: List[CodingItem]


class IssueItem(BaseModel):
    severity: str
    code: str
    details: Details
    diagnostics: str


class Outcome(BaseModel):
    resourceType: str
    text: Text
    issue: List[IssueItem]


class Response(BaseModel):
    status: str
    location: str
    etag: str
    outcome: Outcome
    lastModified: Optional[str] = None


class EntryItem(BaseModel):
    response: Response


class AppointmentRequest(BaseModel):
    resourceType: str
    id: str
    type: str
    link: List[LinkItem]
    entry: List[EntryItem]

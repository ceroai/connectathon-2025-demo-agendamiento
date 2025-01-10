from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Meta(BaseModel):
    versionId: str
    lastUpdated: str
    source: str
    profile: List[str]


class Text(BaseModel):
    status: str
    div: str


class ExtensionItem(BaseModel):
    url: str
    valueCode: str


class NameItem(BaseModel):
    family: str
    given: List[str]


class CodingItem(BaseModel):
    system: str
    code: str
    display: str


class Code(BaseModel):
    coding: List[CodingItem]
    text: str


class QualificationItem(BaseModel):
    code: Code


class Practitioner(BaseModel):
    resourceType: str
    id: str
    meta: Meta
    text: Text
    extension: List[ExtensionItem]
    name: List[NameItem]
    qualification: List[QualificationItem]

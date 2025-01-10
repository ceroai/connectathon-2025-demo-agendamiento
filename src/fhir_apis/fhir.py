import json

import requests

from models.appointment import Appointment
from models.practitioner import Practitioner
from settings import settings
from fhir_apis.auth import get_access_token


with open("fhir_apis/body_solicitar_cita.json", "r") as file:
    body_solicitar_cita_str = json.load(file)


def get_solicitar_cita_body(json_content: dict, patient_id: str) -> dict:
    content = json_content

    # Reemplazar todas las ocurrencias de {patientId}
    for entry in content["entry"]:
        # Reemplazar en fullUrl si contiene {patientId}
        if "{patientId}" in entry["fullUrl"]:
            entry["fullUrl"] = entry["fullUrl"].replace("{patientId}", patient_id)

        # Reemplazar en request.url si existe
        if "request" in entry and "{patientId}" in entry["request"]["url"]:
            entry["request"]["url"] = entry["request"]["url"].replace(
                "{patientId}", patient_id
            )

        # Reemplazar en subject.reference si existe
        if "resource" in entry:
            resource = entry["resource"]
            if "subject" in resource:
                if "{patientId}" in resource["subject"]["reference"]:
                    resource["subject"]["reference"] = resource["subject"][
                        "reference"
                    ].replace("{patientId}", patient_id)

            # Reemplazar en beneficiary.reference si existe (para Coverage)
            if "beneficiary" in resource:
                if "{patientId}" in resource["beneficiary"]["reference"]:
                    resource["beneficiary"]["reference"] = resource["beneficiary"][
                        "reference"
                    ].replace("{patientId}", patient_id)

    return content


def solicitar_cita(patient_id: str) -> requests.Response:
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        settings.FHIR_API_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        json=get_solicitar_cita_body(body_solicitar_cita_str, patient_id),
    )


def obtener_ultima_cita(patient_rut: str = "99.999.999-9") -> Appointment:
    params = {"status": "booked", "patient.identifier": patient_rut}

    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    response = requests.get(
        f"{settings.FHIR_API_URL}/Appointment",
        headers={"Authorization": f"Bearer {access_token}"},
        params=params,
    )
    return Appointment(**response.json())


def get_practitioner(practitioner_id: str) -> Practitioner:
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    response = requests.get(
        f"{settings.FHIR_API_URL}/Practitioner/{practitioner_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return Practitioner(**response.json())


def aceptar_cita(appointment_id: str, patient_id: str, service_request_id: str, practitioner_id: str) -> requests.Response:
    json = {
        "resourceType": "Bundle",
        "id": "BundResp",
        "meta": {
            "profile": [
                "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/BundleRespuesta"
            ]
        },
        "identifier": {
            "value": "BundResp"
        },
        "type": "transaction",
        "timestamp": "2024-07-26T14:15:00-03:00",
        "entry": [
            {
                "fullUrl": "urn:uuid:8a7bac00-3b61-4846-b32f-ad1ec3c46a2c",
                "resource": {
                    "resourceType": "AppointmentResponse",
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/CitaRespuesta"
                        ]
                    },
                    "appointment": {
                        "reference": appointment_id
                    },
                    "actor": {
                        "reference": patient_id
                    },
                    "participantStatus": "accepted"
                },
                "request": {
                    "method": "POST",
                    "url": "AppointmentResponse/"
                }
            },
            {
                "fullUrl": f"{settings.FHIR_API_URL}/{appointment_id}",
                "resource": {
                    "resourceType": "Appointment",
                    "id": "EjemploCita1",
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/Cita"
                        ]
                    },
                    "text": {
                        "status": "extensions",
                        "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p class=\"res-header-id\"><b>Generated Narrative: Appointment EjemploCita1</b></p><a name=\"EjemploCita1\"> </a><a name=\"hcEjemploCita1\"> </a><a name=\"EjemploCita1-es-CL\"> </a><p><b>Apellido Servicio</b>: Comentario de la cita</p><p><b>status</b>: Booked</p><p><b>specialty</b>: <span title=\"Codes:{http://snomed.info/sct 408467006}\">Adult mental illness - specialty (qualifier value)</span></p><p><b>start</b>: 2024-07-25 12:30:00-0300</p><p><b>end</b>: 2024-07-25 12:50:00-0300</p><p><b>basedOn</b>: <a href=\"ServiceRequest-EjemploSolicitudServicio1.html\">ServiceRequest: status = active; intent = order; priority = routine; authoredOn = 2024-07-20 12:00:00-0300</a></p><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href=\"Patient-EjemploPaciente1.html\">Valentina Daniela Contreras  (no stated gender), DoB: 2001-02-10 ( 20.706.399-1)</a></p><p><b>required</b>: Required</p><p><b>status</b>: Accepted</p></blockquote><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href=\"Practitioner-EjemploPrestador1.html\">Practitioner Cuevas Antonia </a></p><p><b>required</b>: Optional</p><p><b>status</b>: Accepted</p></blockquote></div>"
                    },
                    "extension": [
                        {
                            "url": "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/ApellidoServicio",
                            "valueString": "Comentario de la cita"
                        }
                    ],
                    "status": "booked",
                    "specialty": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "394802001"
                                }
                            ]
                        }
                    ],
                    "start": "2024-12-05T14:00:00-03:00",
                    "end": "2024-12-05T14:15:00-03:00",
                    "basedOn": [
                        {
                            "reference": service_request_id
                        }
                    ],
                    "participant": [
                        {
                            "actor": {
                                "reference": patient_id
                            },
                            "required": "required",
                            "status": "accepted"
                        },
                        {
                            "actor": {
                                "reference": practitioner_id
                            },
                            "required": "optional",
                            "status": "accepted"
                        }
                    ]
                },
                "request": {
                    "method": "PUT",
                    "url": appointment_id
                }
            }
        ]
    }

    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        f"{settings.FHIR_API_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json,
    )


def rechazar_cita(appointment_id: str, patient_id: str, service_request_id: str, practitioner_id: str) -> requests.Response:
    json = {
        "resourceType": "Bundle",
        "id": "BundResp",
        "meta": {
            "profile": [
                "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/BundleRespuesta"
            ]
        },
        "identifier": {
            "value": "BundResp"
        },
        "type": "transaction",
        "timestamp": "2024-07-26T14:15:00-03:00",
        "entry": [
            {
                "fullUrl": "urn:uuid:8a7bac00-3b61-4846-b32f-ad1ec3c46a2c",
                "resource": {
                    "resourceType": "AppointmentResponse",
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/CitaRespuesta"
                        ]
                    },
                    "appointment": {
                        "reference": appointment_id
                    },
                    "actor": {
                        "reference": patient_id
                    },
                    "participantStatus": "declined"
                },
                "request": {
                    "method": "POST",
                    "url": "AppointmentResponse/"
                }
            },
            {
                "fullUrl": f"{settings.FHIR_API_URL}/{appointment_id}",
                "resource": {
                    "resourceType": "Appointment",
                    "id": "EjemploCita1",
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/Cita"
                        ]
                    },
                    "text": {
                        "status": "extensions",
                        "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p class=\"res-header-id\"><b>Generated Narrative: Appointment EjemploCita1</b></p><a name=\"EjemploCita1\"> </a><a name=\"hcEjemploCita1\"> </a><a name=\"EjemploCita1-es-CL\"> </a><p><b>Apellido Servicio</b>: Comentario de la cita</p><p><b>status</b>: Booked</p><p><b>specialty</b>: <span title=\"Codes:{http://snomed.info/sct 408467006}\">Adult mental illness - specialty (qualifier value)</span></p><p><b>start</b>: 2024-07-25 12:30:00-0300</p><p><b>end</b>: 2024-07-25 12:50:00-0300</p><p><b>basedOn</b>: <a href=\"ServiceRequest-EjemploSolicitudServicio1.html\">ServiceRequest: status = active; intent = order; priority = routine; authoredOn = 2024-07-20 12:00:00-0300</a></p><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href=\"Patient-EjemploPaciente1.html\">Valentina Daniela Contreras  (no stated gender), DoB: 2001-02-10 ( 20.706.399-1)</a></p><p><b>required</b>: Required</p><p><b>status</b>: Accepted</p></blockquote><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href=\"Practitioner-EjemploPrestador1.html\">Practitioner Cuevas Antonia </a></p><p><b>required</b>: Optional</p><p><b>status</b>: Accepted</p></blockquote></div>"
                    },
                    "extension": [
                        {
                            "url": "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/ApellidoServicio",
                            "valueString": "Comentario de la cita"
                        }
                    ],
                    "status": "booked",
                    "specialty": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "394802001"
                                }
                            ]
                        }
                    ],
                    "start": "2024-12-05T14:00:00-03:00",
                    "end": "2024-12-05T14:15:00-03:00",
                    "basedOn": [
                        {
                            "reference": service_request_id
                        }
                    ],
                    "participant": [
                        {
                            "actor": {
                                "reference": patient_id
                            },
                            "required": "required",
                            "status": "accepted"
                        },
                        {
                            "actor": {
                                "reference": practitioner_id
                            },
                            "required": "optional",
                            "status": "accepted"
                        }
                    ]
                },
                "request": {
                    "method": "PUT",
                    "url": appointment_id
                }
            }
        ]
    }

    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        f"{settings.FHIR_API_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json,
    )
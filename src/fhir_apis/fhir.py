import json
import uuid
import requests
import datetime
from models.appointment import Appointment
from models.single_appointment import SingleAppointment
from models.appointment_create_request import PostAppointmentRequest
from models.practitioner import Practitioner
from settings import settings
from fhir_apis.auth import get_access_token


def solicitar_cita(
    patient_id: str, observation: str | None = None
) -> requests.Response:
    json = {
        "resourceType": "Bundle",
        "id": "BundSol",
        "meta": {
            "profile": [
                "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/BundleSolicitud"
            ]
        },
        "identifier": {"value": "BundSol"},
        "type": "transaction",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "entry": [
            {
                "fullUrl": f"https://gateway.onfhir.cl/hl7cl/fhir/{patient_id}",
                "resource": {
                    "resourceType": "Patient",
                    "id": "PacienteGrupo12",
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/PacienteAgenda"
                        ]
                    },
                    "text": {
                        "status": "generated",
                        "div": '<div xmlns="http://www.w3.org/1999/xhtml"><p class="res-header-id"><b>Generated Narrative: Patient EjemploPaciente1</b></p><a name="EjemploPaciente1"> </a><a name="hcEjemploPaciente1"> </a><a name="EjemploPaciente1-es-CL"> </a><p style="border: 1px #661aff solid; background-color: #e6e6ff; padding: 10px;">Valentina Daniela Contreras  (no stated gender), DoB: 2001-02-10 ( 20.706.399-1)</p><hr/><table class="grid"><tr><td style="background-color: #f3f5da" title="Da la edad del paciente"><a href="StructureDefinition-Edad.html">Edad del paciente</a></td><td colspan="3">23</td></tr></table></div>',
                    },
                    "identifier": [{"value": "99.999.999-9"}],
                    "name": [
                        {"family": "Organa de la Vega", "given": ["Mohana", "Leia"]}
                    ],
                    "birthDate": "1982-11-07",
                },
                "request": {"method": "PUT", "url": patient_id},
            },
            {
                "fullUrl": "urn:uuid:8a7b4900-3861-4849-b36f-ad1ec3c46a2f",
                "resource": {
                    "resourceType": "ServiceRequest",
                    "id": str(uuid.uuid4()),
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/SolicitudServicio"
                        ]
                    },
                    "status": "active",
                    "intent": "directive",
                    "priority": "routine",
                    "subject": {"reference": patient_id},
                    "authoredOn": "2024-12-03T17:00:00-03:00",
                    "reasonReference": [
                        {"reference": "urn:uuid:8a7b4901-3862-4649-b66f-ac1eb3c4aa2f"},
                        {"reference": "urn:uuid:8a7b4901-3862-4649-b66f-ac1ec3a4aa2f"},
                    ],
                },
                "request": {"method": "POST", "url": "ServiceRequest/"},
            },
            {
                "fullUrl": "urn:uuid:8a7b4901-3862-4649-b66f-ac1ec3c4aa2f",
                "resource": {
                    "resourceType": "Coverage",
                    "id": str(uuid.uuid4()),
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/Prevision"
                        ]
                    },
                    "text": {
                        "status": "generated",
                        "div": '<div xmlns="http://www.w3.org/1999/xhtml"><p class="res-header-id"><b>Generated Narrative: Coverage EjemploPrevison</b></p><a name="EjemploPrevison"> </a><a name="hcEjemploPrevison"> </a><a name="EjemploPrevison-es-CL"> </a><p><b>status</b>: Active</p><p><b>type</b>: <span title="Codes:{https://interoperabilidad.minsal.cl/fhir/ig/agenda/CodeSystem/CSPrevision 01}">FONASA</span></p><p><b>beneficiary</b>: <a href="Patient-EjemploPaciente1.html">Valentina Daniela Contreras  (no stated gender), DoB: 2001-02-10 ( 20.706.399-1)</a></p><p><b>payor</b>: Tramo B</p></div>',
                    },
                    "status": "active",
                    "type": {
                        "coding": [
                            {
                                "system": "https://interoperabilidad.minsal.cl/fhir/ig/agenda/CodeSystem/CSPrevision",
                                "code": "01",
                                "display": "FONASA",
                            }
                        ]
                    },
                    "beneficiary": {"reference": patient_id},
                    "payor": [{"display": "Tramo B"}],
                },
                "request": {"method": "POST", "url": "Coverage/"},
            },
            {
                "fullUrl": "urn:uuid:8a7b4901-3862-4649-b66f-ac1ec3a4aa2f",
                "resource": {
                    "resourceType": "Condition",
                    "meta": {
                        "profile": [
                            "https://hl7chile.cl/fhir/ig/clcore/StructureDefinition/CoreDiagnosticoCl"
                        ]
                    },
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                                "display": "Active",
                            }
                        ],
                        "text": "Activo",
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                                "display": "Confirmed",
                            }
                        ],
                        "text": "Confirmado",
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "394802001",
                                "display": "Diabetic retinopathy",
                            }
                        ],
                        "text": "Diagnóstico de diabetes retinopática",
                    },
                    "subject": {"reference": patient_id},
                    "onsetDateTime": "2017-08-07T00:00:00-04:00",
                },
                "request": {"method": "POST", "url": "Condition/"},
            },
            {
                "fullUrl": "urn:uuid:8a7b4901-3862-4649-b66f-ac1eb3c4aa2f",
                "resource": {
                    "resourceType": "Observation",
                    "meta": {
                        "profile": [
                            "https://hl7chile.cl/fhir/ig/clcore/StructureDefinition/CoreObservacionCL"
                        ]
                    },
                    "status": "registered",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "10210-3",
                                "display": "Narrativa General de problema físico",
                            }
                        ],
                        "text": "Narrativa General de problema físico",
                    },
                    "note": [{"text": observation or ""}],
                    "subject": {"reference": patient_id},
                    "effectiveDateTime": "2024-11-23T17:00:00-03:00",
                },
                "request": {"method": "POST", "url": "Observation/"},
            },
        ],
    }
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        settings.FHIR_API_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        json=json,
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


def obtener_cita_por_service_request_id(service_request_id: str) -> Appointment:
    params = {"based-on": service_request_id, "status": "booked"}

    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    response = requests.get(
        f"{settings.FHIR_API_URL}/Appointment",
        headers={"Authorization": f"Bearer {access_token}"},
        params=params,
    )
    return Appointment(**response.json())


with open("fhir_apis/body_crear_cita.json", "r") as file:
    body_crear_cita = json.load(file)


def aceptar_cita(
    appointment_id: str, patient_id: str, service_request_id: str, practitioner_id: str
) -> requests.Response:
    json = {
        "resourceType": "Bundle",
        "id": "BundResp",
        "meta": {
            "profile": [
                "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/BundleRespuesta"
            ]
        },
        "identifier": {"value": "BundResp"},
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
                    "appointment": {"reference": appointment_id},
                    "actor": {"reference": patient_id},
                    "participantStatus": "accepted",
                },
                "request": {"method": "POST", "url": "AppointmentResponse/"},
            },
            {
                "fullUrl": f"{settings.FHIR_API_URL}/{appointment_id}",
                "resource": {
                    "resourceType": "Appointment",
                    "id": str(uuid.uuid4()),
                    "meta": {
                        "profile": [
                            "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/Cita"
                        ]
                    },
                    "text": {
                        "status": "extensions",
                        "div": '<div xmlns="http://www.w3.org/1999/xhtml"><p class="res-header-id"><b>Generated Narrative: Appointment EjemploCita1</b></p><a name="EjemploCita1"> </a><a name="hcEjemploCita1"> </a><a name="EjemploCita1-es-CL"> </a><p><b>Apellido Servicio</b>: Comentario de la cita</p><p><b>status</b>: Booked</p><p><b>specialty</b>: <span title="Codes:{http://snomed.info/sct 408467006}">Adult mental illness - specialty (qualifier value)</span></p><p><b>start</b>: 2024-07-25 12:30:00-0300</p><p><b>end</b>: 2024-07-25 12:50:00-0300</p><p><b>basedOn</b>: <a href="ServiceRequest-EjemploSolicitudServicio1.html">ServiceRequest: status = active; intent = order; priority = routine; authoredOn = 2024-07-20 12:00:00-0300</a></p><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href="Patient-EjemploPaciente1.html">Valentina Daniela Contreras  (no stated gender), DoB: 2001-02-10 ( 20.706.399-1)</a></p><p><b>required</b>: Required</p><p><b>status</b>: Accepted</p></blockquote><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href="Practitioner-EjemploPrestador1.html">Practitioner Cuevas Antonia </a></p><p><b>required</b>: Optional</p><p><b>status</b>: Accepted</p></blockquote></div>',
                    },
                    "extension": [
                        {
                            "url": "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/ApellidoServicio",
                            "valueString": "Comentario de la cita",
                        }
                    ],
                    "status": "booked",
                    "specialty": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "394802001",
                                }
                            ]
                        }
                    ],
                    "start": "2024-12-05T14:00:00-03:00",
                    "end": "2024-12-05T14:15:00-03:00",
                    "basedOn": [{"reference": service_request_id}],
                    "participant": [
                        {
                            "actor": {"reference": patient_id},
                            "required": "required",
                            "status": "accepted",
                        },
                        {
                            "actor": {"reference": practitioner_id},
                            "required": "optional",
                            "status": "accepted",
                        },
                    ],
                },
                "request": {"method": "PUT", "url": appointment_id},
            },
        ],
    }
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        f"{settings.FHIR_API_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json,
    )


def get_crear_cita_body(body_crear_cita: dict, request: PostAppointmentRequest) -> dict:
    id = str(uuid.uuid4())
    body_crear_cita["id"] = id
    body_crear_cita["status"] = request.status
    body_crear_cita["specialty"][0]["coding"] = [
        item.model_dump() for item in request.specialty
    ]
    body_crear_cita["start"] = request.start.isoformat()
    body_crear_cita["end"] = request.end.isoformat()
    body_crear_cita["basedOn"] = [{"reference": request.service_request_id}]
    body_crear_cita["participant"][0]["actor"]["reference"] = request.patient_id
    body_crear_cita["participant"][1]["actor"]["reference"] = request.practitioner_id

    return body_crear_cita


def crear_cita(request: PostAppointmentRequest) -> requests.Response:
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        f"{settings.FHIR_API_URL}Appointment",
        headers={"Authorization": f"Bearer {access_token}"},
        json=get_crear_cita_body(body_crear_cita, request),
    )


def rechazar_cita(
    appointment_id: str, patient_id: str, service_request_id: str, practitioner_id: str
) -> requests.Response:
    json = {
        "resourceType": "Bundle",
        "id": "BundResp",
        "meta": {
            "profile": [
                "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/BundleRespuesta"
            ]
        },
        "identifier": {"value": "BundResp"},
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
                    "appointment": {"reference": appointment_id},
                    "actor": {"reference": patient_id},
                    "participantStatus": "declined",
                },
                "request": {"method": "POST", "url": "AppointmentResponse/"},
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
                        "div": '<div xmlns="http://www.w3.org/1999/xhtml"><p class="res-header-id"><b>Generated Narrative: Appointment EjemploCita1</b></p><a name="EjemploCita1"> </a><a name="hcEjemploCita1"> </a><a name="EjemploCita1-es-CL"> </a><p><b>Apellido Servicio</b>: Comentario de la cita</p><p><b>status</b>: Booked</p><p><b>specialty</b>: <span title="Codes:{http://snomed.info/sct 408467006}">Adult mental illness - specialty (qualifier value)</span></p><p><b>start</b>: 2024-07-25 12:30:00-0300</p><p><b>end</b>: 2024-07-25 12:50:00-0300</p><p><b>basedOn</b>: <a href="ServiceRequest-EjemploSolicitudServicio1.html">ServiceRequest: status = active; intent = order; priority = routine; authoredOn = 2024-07-20 12:00:00-0300</a></p><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href="Patient-EjemploPaciente1.html">Valentina Daniela Contreras  (no stated gender), DoB: 2001-02-10 ( 20.706.399-1)</a></p><p><b>required</b>: Required</p><p><b>status</b>: Accepted</p></blockquote><blockquote><p><b>participant</b></p><p><b>actor</b>: <a href="Practitioner-EjemploPrestador1.html">Practitioner Cuevas Antonia </a></p><p><b>required</b>: Optional</p><p><b>status</b>: Accepted</p></blockquote></div>',
                    },
                    "extension": [
                        {
                            "url": "https://interoperabilidad.minsal.cl/fhir/ig/agenda/StructureDefinition/ApellidoServicio",
                            "valueString": "Comentario de la cita",
                        }
                    ],
                    "status": "booked",
                    "specialty": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "394802001",
                                }
                            ]
                        }
                    ],
                    "start": "2024-12-05T14:00:00-03:00",
                    "end": "2024-12-05T14:15:00-03:00",
                    "basedOn": [{"reference": service_request_id}],
                    "participant": [
                        {
                            "actor": {"reference": patient_id},
                            "required": "required",
                            "status": "accepted",
                        },
                        {
                            "actor": {"reference": practitioner_id},
                            "required": "optional",
                            "status": "accepted",
                        },
                    ],
                },
                "request": {"method": "PUT", "url": appointment_id},
            },
        ],
    }

    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        f"{settings.FHIR_API_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json,
    )


def get_practitioner(practitioner_id: str) -> Practitioner:
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    response = requests.get(
        f"{settings.FHIR_API_URL}/Practitioner/{practitioner_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return Practitioner(**response.json())


def get_appointment_by_id(appointment_id: str) -> SingleAppointment:
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    response = requests.get(
        f"{settings.FHIR_API_URL}/Appointment/{appointment_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return SingleAppointment(**response.json())


def obtener_solicitudes(patient_id: str | None) -> list[dict]:
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    params = {"subject": patient_id} if patient_id else None
    response = requests.get(
        f"{settings.FHIR_API_URL}/ServiceRequest",
        params=params,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()["entry"]

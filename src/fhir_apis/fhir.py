import json

import requests

from models.accept_reject_appointment import AcceptAppointment
from models.appointment import Appointment
from models.practitioner import Practitioner
from settings import settings


def get_access_token(token_url: str, client_id: str, client_secret: str) -> str:
    """
    Obtiene un token de acceso usando las credenciales del cliente
    """
    response = requests.post(
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "openid profile",
        },
    )
    response.raise_for_status()  # Lanza una excepción si hay error
    return response.json()["access_token"]


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


def accept_or_reject_appointment(accept_appointment_body: AcceptAppointment) -> requests.Response:
    access_token = get_access_token(
        settings.FHIR_AUTH_URL, settings.CLIENT_ID, settings.CLIENT_SECRET
    )
    return requests.post(
        f"{settings.FHIR_API_URL}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=accept_appointment_body.model_dump(),
    )

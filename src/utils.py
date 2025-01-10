from datetime import datetime

import locale

from models.single_appointment import SingleAppointment
from models.practitioner import Practitioner


def formatear_fecha_legible(fecha_str: str) -> str:
    """
    Convierte una fecha ISO 8601 a un formato legible en español

    Args:
        fecha_str: String de fecha en formato ISO (ej: '2024-07-25T12:30:00-03:00')

    Returns:
        String con la fecha en formato legible (ej: 'El jueves 25 de julio de 2024 a las 12:30 horas')
    """
    # Configurar locale a español
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

    # Convertir string a objeto datetime
    fecha = datetime.fromisoformat(fecha_str)

    # Formatear la fecha
    dia_semana = fecha.strftime("%A").lower()
    dia = fecha.day
    mes = fecha.strftime("%B").lower()
    año = fecha.year
    hora = fecha.strftime("%H:%M")

    return f"El {dia_semana} {dia} de {mes} de {año} a las {hora} horas"


def find_appointment_id(appointment: SingleAppointment) -> str:
    return appointment.id


def find_practitioner_id(appointment: SingleAppointment) -> str:
    for participant in appointment.participant:
        if participant.actor.reference.startswith("Practitioner/"):
            return participant.actor.reference.split("/")[1]
    return None


def find_service_request_id(appointment: SingleAppointment) -> str:
    for based_on in appointment.basedOn:
        if based_on.reference.startswith("ServiceRequest/"):
            return based_on.reference.split("/")[1]
    return None


def find_patient_id(appointment: SingleAppointment) -> str:
    for participant in appointment.participant:
        if participant.actor.reference.startswith("Patient/"):
            return participant.actor.reference.split("/")[1]
    return None


def get_practitioner_name(practitioner: Practitioner) -> str:
    return f"{practitioner.name[0].given[0]} {practitioner.name[0].family}"


def find_service_request_id_from_response(response: dict) -> str | None:
    for entry in response["entry"]:
        if entry["response"]["status"] == "201 Created":
            pieces = entry["response"]["location"].split("/")
            if pieces[0] == "ServiceRequest":
                return pieces[1]

    return None

from datetime import datetime

import locale

from models.appointment import Appointment
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


def find_appointment_id(appointment: Appointment) -> str:
    for entry in appointment.entry:
        if entry.resource.id:
            return entry.resource.id
    return None


def find_practitioner_id(appointment: Appointment) -> str:
    for entry in appointment.entry:
        for participant in entry.resource.participant:
            if participant.actor.reference.startswith("Practitioner/"):
                return participant.actor.reference.split("/")[1]
    return None


def find_service_request_id(appointment: Appointment) -> str:
    for entry in appointment.entry:
        for based_on in entry.resource.basedOn:
            if based_on.reference.startswith("ServiceRequest/"):
                return based_on.reference.split("/")[1]
    return None


def find_patient_id(appointment: Appointment) -> str:
    for entry in appointment.entry:
        if entry.resource.actor.reference.startswith("Patient/"):
            return entry.resource.actor.reference.split("/")[1]
    return None


def get_practitioner_name(practitioner: Practitioner) -> str:
    return f"{practitioner.name[0].given[0]} {practitioner.name[0].family}"

from datetime import datetime
import locale


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

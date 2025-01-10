
# Demo Asignación de citas usando WhatsApp y APIs FHIR

Este servicio proporciona una API para la gestión de citas médicas utilizando el estándar FHIR (Fast Healthcare Interoperability Resources).

## Descripción

Este proyecto implementa un servicio de gestión de citas médicas que se integra con sistemas FHIR. Permite la creación, consulta y gestión de citas médicas siguiendo los estándares de interoperabilidad en salud.

## Requisitos

- Python 3.12
- Dependencias listadas en `pyproject.toml`

## Instalación

Instala las dependencias utilizando uv:

```bash
uv venv
source .venv/bin/activate
uv pip install .
```

Configura las variables de entorno:
- Copia el archivo `src/.env.example` a `src/.env`
- Ajusta las variables según tu entorno

Configura una cuenta de whatsapp en Twilio, y en el .env pon las credenciales correspondientes.

Si ejecutas el servidor localmente, deberás exponer el puerto 8000 a internet (por ej., con ngrok), y configurar el webhook de Twilio para que apunte a tu servidor.

## Uso

1. Inicia el servidor:

```bash
python src/main.py
```

Luego puedes escribir al whatsapp que tienes configurado en el archivo `.env` y te asignará una cita.
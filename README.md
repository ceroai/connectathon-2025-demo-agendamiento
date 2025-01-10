
# Demo Asignación de citas usando WhatsApp y APIs FHIR

Este servicio proporciona una API para la gestión de citas médicas utilizando el estándar FHIR (Fast Healthcare Interoperability Resources).

![Demo Connectathon](demo-connectathon-2.mp4)

## Descripción

Este proyecto implementa un servicio de gestión de citas médicas que se integra con sistemas FHIR. Permite la creación, consulta y gestión de citas médicas siguiendo los estándares de interoperabilidad en salud.

## Requisitos

- Python 3.12
- Dependencias listadas en `pyproject.toml`

## Instalación

1. Clona el repositorio

2. Instala las dependencias utilizando uv:

```bash
uv venv
uv sync
source .venv/bin/activate
```

3. Configura las variables de entorno:
   - Copia el archivo `src/.env.example` a `src/.env`
   - Ajusta las variables según tu entorno


## Uso

1. Inicia el servidor:

```bash
python src/main.py
```

Luego puedes escribir al whatsapp que tienes configurado en el archivo `.env` y te asignará una cita.

## Servidor FHIR

Si no tienes un servidor FHIR, puedes levantar uno localmente con docker. Por ejemplo, `hapiproject/hapi` y usar la url base en los settings del proyecto. 
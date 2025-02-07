import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

import requests
import uvicorn
from fastapi import FastAPI, Request, Response
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse

from fhir_apis.fhir import (
    aceptar_cita,
    crear_cita,
    get_practitioner,
    obtener_solicitudes,
    rechazar_cita,
    solicitar_cita,
    get_appointment_by_id,
)
from models.appointment_create_request import PostAppointmentRequest
from models.single_appointment import SingleAppointment
from settings import settings
from utils import (
    find_appointment_id,
    find_patient_id,
    find_practitioner_id,
    find_service_request_id,
    formatear_fecha_legible,
    get_practitioner_name,
    find_service_request_id_from_response,
)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

app = FastAPI(debug=True)

# Store conversation history: phone_number -> list of messages
conversations: Dict[str, List[dict]] = {}

# Store appointments: phone_number -> appointment
appointments: Dict[str, dict] = {}

PATIENT_ID = "Patient/781"
# PATIENT_ID = "Patient/888"

system_prompt = f"""
    Eres un asistente del consultorio familiar llamado "El Consultorio", ubicado en Av. Los Montt 2301 en Puerto Montt, región de Los Lagos, cuyas horas de funcionamiento son desde las 8:00 hasta las 17 hrs. Los consultorios también se conocen como CESFAM, o Centro de Salud Familiar. 
    
    Tu labor es ayudar a pacientes a pedir citas con el doctor. Los pacientes no pueden agendar cuando quieran, sino que deben solicitar una cita, y el CESFAM se encarga de asignar una cita a los pacientes. En este contexto, las citas también se les llama "horas", por ejemplo, cuando el paciente dice "quiero agendar una hora", la "hora" es una cita médica.
    
    Cuando el paciente escriba algo con la intención de agendar una cita, junto con sus síntomas, responde con "AGENDAR" más los síntomas que el paciente indique. Si el paciente no indica síntomas, pregúntale por ellos. Sólo cuando el paciente haya indicado los síntomas, debes responder con "AGENDAR " más los síntomas. Nota que es "AGENDAR" con un espacio, y luego el texto con los síntomas, sin decir nada más (por ejemplo, no digas "AGENDAR síntomas: dolor estomacal", sino que "AGENDAR dolor estomacal"). Si no hay intención de agendar, intenta ayudar al paciente con su consulta.

    Sólo después de haber dicho 'AGENDAR', el paciente puede aceptar o rechazar la cita. Aceptar la cita significa que el paciente confirma que asistirá a la cita asignada. Rechazar la cita significa que el paciente no puede asistir a la cita asignada. Cuando ocurra la aceptación o rechazo, debes responder "ACEPTADO" o "RECHAZADO" respectivamente, sin decir nada más. Si el paciente rechaza la cita, además puede indicar en su mensaje que le gustaría cambiar la fecha (por ejemplo, "no puedo asistir, es posible ir la próxima semana?"). En ese caso, debes responder "REASIGNAR" seguido de la fecha que eligió, por ejemplo: "REASIGNAR 2025-01-01".
    
    La fecha y hora actual es {datetime.now().isoformat()}.
"""


def cleanup_old_conversations():
    """Remove conversations and appointments older than CONVERSATION_TIMEOUT minutes"""
    current_time = datetime.now()
    numbers_to_remove = []

    for phone_number, messages in conversations.items():
        if messages:
            last_message_time = messages[-1].get("timestamp")
            if last_message_time and (current_time - last_message_time) > timedelta(
                minutes=settings.CONVERSATION_TIMEOUT
            ):
                numbers_to_remove.append(phone_number)

    for number in numbers_to_remove:
        del conversations[number]
        if number in appointments:
            del appointments[number]


def _generate_appointment_message(
    appointment_datetime: str, practitioner_name: str, observation: str
) -> str:
    return f"""Te asignamos la siguiente cita:

🗓 Fecha y hora: *{appointment_datetime}*
🥼 Profesional: {practitioner_name}
🏥 Sucursal: El Consultorio
📍 Ubicación: Av. Los Montt 2301, Puerto Montt
🤒 Síntomas reportados: {observation}

Por favor confirma tu asistencia respondiendo a este mensaje. 

¡Nos vemos pronto! 🏥👩‍⚕️"""


async def get_ai_response(message: str, conversation_history: List[dict]) -> str:
    try:
        # Build the messages list including conversation history
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        for msg in conversation_history:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the current message
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o", messages=messages, max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "Sorry, I'm having trouble processing your message right now."


@app.post("/webhook")
async def webhook(request: Request):
    # Clean up old conversations
    cleanup_old_conversations()

    # Get the form data from the Twilio webhook
    form_data = await request.form()

    # Extract the message body and sender's WhatsApp number
    incoming_msg = form_data.get("Body", "").lower()
    sender = form_data.get("From", "")

    # Initialize conversation history for new users
    if sender not in conversations:
        conversations[sender] = []

    # Create a TwiML response
    resp = MessagingResponse()

    if incoming_msg:
        # Add user message to conversation history
        conversations[sender].append(
            {"role": "user", "content": incoming_msg, "timestamp": datetime.now()}
        )

        # Get AI-generated response
        ai_response = await get_ai_response(incoming_msg, conversations[sender])

        # Add AI response to conversation history
        conversations[sender].append(
            {"role": "assistant", "content": ai_response, "timestamp": datetime.now()}
        )

        # Keep only the last 10 messages to prevent memory overflow
        if len(conversations[sender]) > 10:
            conversations[sender] = conversations[sender][-10:]

        match ai_response:
            # case "AGENDAR":
            #     resp.message(
            #         "Por favor, indica los síntomas de la consulta"
            #     )
            #     # Store the appointment request
            #     appointments[sender] = {
            #         "patient_id": PATIENT_ID,
            #         "status": "pending",
            #         "observation": "",
            #     }
            case str() if ai_response.startswith("AGENDAR "):
                observation = ai_response.split(" ", 1)[1]
                response = solicitar_cita(PATIENT_ID, observation)
                service_request_id = find_service_request_id_from_response(response.json())
                if response.ok:
                    resp.message(
                        f"Estamos pidiendo la cita, te avisaremos cuando esté agendada. El código de solicitud es {service_request_id}"
                    )
                    # Store the appointment request
                    appointments[sender] = {
                        "patient_id": PATIENT_ID,
                        "status": "pending",
                        "observation": observation,
                    }
                else:
                    resp.message(
                        "Hubo un error al agendar la cita, envía un correo a ministra@minsal.cl"
                    )
            case "ACEPTADO":
                cita = SingleAppointment(**appointments[sender]["appointment"])

                aceptar_cita(
                    appointment_id=find_appointment_id(cita),
                    patient_id=find_patient_id(cita),
                    service_request_id=find_service_request_id(cita),
                    practitioner_id=find_practitioner_id(cita),
                )

                resp.message("Gracias por su respuesta, te esperamos!")
            case "RECHAZADO":
                cita = SingleAppointment(**appointments[sender]["appointment"])
                rechazar_cita(
                    appointment_id=find_appointment_id(cita),
                    patient_id=find_patient_id(cita),
                    service_request_id=find_service_request_id(cita),
                    practitioner_id=find_practitioner_id(cita),
                )

                resp.message("Rechazaste la cita.")

            case "REASIGNAR":
                resp.message(ai_response)
            case str() if ai_response.startswith("REASIGNAR "):
                try:
                    fecha = ai_response.split(" ")[1]
                    # TODO: Implementar lógica para reasignar cita
                    resp.message(
                        f"Veremos si es posible reagendar la cita para una fecha cercana al {fecha}. Te avisaremos por acá la nueva asignación."
                    )
                except IndexError:
                    resp.message("Por favor indica la fecha en formato YYYY-MM-DD")
            case _:
                resp.message(ai_response)
    else:
        resp.message("Hello! Thanks for reaching out!")

    # Return the TwiML response
    return Response(content=str(resp), media_type="application/xml")


@app.post("/appointment")
async def create_appointment(body: PostAppointmentRequest):
    response = crear_cita(body)

    appointment_id = response.json()["id"]

    # get patient id from response
    participants = response.json()["participant"]
    for participant in participants:
        if participant["actor"]["reference"].startswith("Patient/"):
            patient_id = participant["actor"]["reference"]
            break

    for sender, data in appointments.items():
        if data["patient_id"] == patient_id:
            # TODO
            appointments[sender]["appointment"] = response.json()
            break
    else:
        return Response(status_code=404, content="Patient not found")

    asyncio.create_task(send_appointment_date(sender, appointment_id, appointments[sender]["observation"]))

    return response.json()


@app.get("/service_requests")
async def get_service_requests(patient_id: str | None) -> list[dict]:
    return obtener_solicitudes(patient_id)


async def send_appointment_date(sender: str, appointment_id: str, observation: str):
    await asyncio.sleep(settings.WAIT_TIME_FOR_APPOINTMENT_SECONDS)

    try:
        # Get the appointment
        cita = get_appointment_by_id(appointment_id)
        # service_request_id = appointments[sender]["appointment"]["basedOn"][0]["reference"].split("/")[1]
        # cita = obtener_cita_por_service_request_id(service_request_id)

        patient_id = find_patient_id(cita)
        practitioner_id = find_practitioner_id(cita)
        practitioner = get_practitioner(practitioner_id)
        fecha_cita = formatear_fecha_legible(cita.start)
        nombre_practitioner = get_practitioner_name(practitioner)

        # Store the confirmed appointment
        appointments[sender] = {
            "patient_id": patient_id,
            "status": "confirmed",
            "appointment": cita.model_dump(),
            "formatted_date": fecha_cita,
            "practitioner_name": nombre_practitioner,
        }

        # Create and send the follow-up message via Twilio
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_number = settings.TWILIO_FROM_NUMBER

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        data = {
            "To": sender,
            "From": from_number,
            "Body": _generate_appointment_message(fecha_cita, nombre_practitioner, observation),
        }

        auth = (account_sid, auth_token)
        requests.post(url, data=data, auth=auth)
    except Exception as e:
        print(f"Error sending follow-up message: {e}")
        if sender in appointments:
            appointments[sender] = {"status": "error"}


def main():
    # Run the FastAPI application using uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

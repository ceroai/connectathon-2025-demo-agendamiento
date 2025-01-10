from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import uvicorn
from datetime import datetime, timedelta
from typing import Dict, List
from fhir_apis.fhir import (
    solicitar_cita,
    obtener_ultima_cita,
    get_practitioner,
    aceptar_cita,
    rechazar_cita,
)
from utils import (
    formatear_fecha_legible,
    get_practitioner_name,
    find_practitioner_id,
    find_service_request_id,
    find_patient_id,
    find_appointment_id,
)
import requests
import asyncio
from settings import settings


# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

app = FastAPI()

# Store conversation history: phone_number -> list of messages
conversations: Dict[str, List[dict]] = {}

# Store appointments: phone_number -> appointment
appointments: Dict[str, dict] = {}

system_prompt = f"""
    Eres un asistente de WhatsApp que ayuda a pacientes a agendar citas con el doctor. Cuando el paciente escriba algo con la intención de agendar una cita, responde con la palabra 'AGENDAR'. No digas nada más. Si no hay intención de agendar, intenta ayudar al paciente con su consulta.

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
            case "AGENDAR":
                response = solicitar_cita("Patient/781")
                if response.ok:
                    resp.message(
                        "Estamos pidiendo la cita, te avisaremos cuando esté agendada"
                    )
                    # Store the appointment request
                    appointments[sender] = {"status": "pending"}
                    # Schedule the follow-up message
                    asyncio.create_task(send_appointment_date(sender))
                else:
                    resp.message(
                        "Hubo un error al agendar la cita, envía un correo a ministra@minsal.cl"
                    )
            case "ACEPTADO":
                cita = obtener_ultima_cita()

                aceptar_cita(
                    appointment_id=find_appointment_id(cita),
                    patient_id=find_patient_id(cita),
                    service_request_id=find_service_request_id(cita),
                    practitioner_id=find_practitioner_id(cita),
                )

                resp.message("Gracias por su respuesta, te esperamos!")
            case "RECHAZADO":
                cita = obtener_ultima_cita()
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
                        f"Estamos reasignando tu cita para el {fecha}, te confirmaremos cuando esté lista"
                    )
                except IndexError:
                    resp.message("Por favor indica la fecha en formato YYYY-MM-DD")
            case _:
                resp.message(ai_response)
    else:
        resp.message("Hello! Thanks for reaching out!")

    # Return the TwiML response
    return Response(content=str(resp), media_type="application/xml")


async def send_appointment_date(sender: str):
    await asyncio.sleep(settings.WAIT_TIME_FOR_APPOINTMENT_SECONDS)

    try:
        # Get the appointment date
        cita = obtener_ultima_cita()
        practitioner_id = find_practitioner_id(cita)
        practitioner = get_practitioner(practitioner_id)
        fecha_cita = formatear_fecha_legible(cita.entry[0].resource.start)
        nombre_practitioner = get_practitioner_name(practitioner)
        # Store the confirmed appointment
        appointments[sender] = {
            "status": "confirmed",
            "appointment": cita.entry[0].resource,
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
            "Body": f"Tu cita ha sido agendada con {nombre_practitioner} para: {fecha_cita}\n\nTe esperamos!",
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

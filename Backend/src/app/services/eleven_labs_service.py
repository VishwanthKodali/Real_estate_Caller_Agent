"""
ElevenLabs service.
- Agent creation: REAL (works on free tier)
- Outbound calls: REAL via Twilio integration (requires phone number ID in ElevenLabs dashboard)
- TTS: REAL (works on free tier)
"""
import httpx
from typing import Optional
from src.app.common import Settings

ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


def _headers():
    return {
        "xi-api-key": Settings.elevenlabs_api_key,
        "Content-Type": "application/json"
    }


# ─── Agent ────────────────────────────────────────────────────────────────────

async def create_agent(
    name: str,
    system_prompt: str,
    first_message: str,
    voice_id: str,
) -> dict:
    """
    Create a real ElevenLabs conversational AI agent.
    Knowledge is embedded directly in system_prompt (no KB needed).
    Works on free tier.
    """
    payload = {
        "name": name,
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": system_prompt
                },
                "first_message": first_message,
                "language": "en"
            },
            "tts": {
                "voice_id": voice_id or "21m00Tcm4TlvDq8ikWAM"  # Default: Rachel
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ELEVENLABS_BASE}/convai/agents/create",
            headers=_headers(),
            json=payload,
            timeout=60.0
        )
        if response.status_code != 200:
            print(f"[ElevenLabs] Agent creation failed {response.status_code}: {response.text}")
            return {"agent_id": None}
        data = response.json()
        print(f"[ElevenLabs] Agent created: {data.get('agent_id')}")
        return data


async def get_agent(agent_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ELEVENLABS_BASE}/convai/agents/{agent_id}",
            headers=_headers(),
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def delete_agent(agent_id: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{ELEVENLABS_BASE}/convai/agents/{agent_id}",
                headers=_headers(),
                timeout=30.0
            )
            return response.status_code in [200, 204]
    except Exception:
        return False


# ─── Outbound Calls ───────────────────────────────────────────────────────────

async def initiate_outbound_call(
    agent_id: str,
    to_number: str,
) -> dict:
    """
    Initiate a real outbound call via ElevenLabs + Twilio.

    Prerequisites:
    1. Go to elevenlabs.io → Agents → Phone Numbers
    2. Add/buy a phone number (connect your Twilio or buy one)
    3. Copy the Phone Number ID and set ELEVENLABS_PHONE_NUMBER_ID in .env
    """
    phone_number_id = Settings.elevenlabs_phone_number_id

    if not phone_number_id:
        raise ValueError(
            "ELEVENLABS_PHONE_NUMBER_ID not configured. "
            "Go to ElevenLabs Dashboard → Agents → Phone Numbers → add a number, "
            "then copy the Phone Number ID into your .env file."
        )

    if not agent_id:
        raise ValueError(
            "No ElevenLabs agent_id for this campaign. "
            "Delete and recreate the campaign to generate a new agent."
        )

    payload = {
        "agent_id": agent_id,
        "agent_phone_number_id": phone_number_id,
        "to_number": to_number
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ELEVENLABS_BASE}/convai/twilio/outbound-call",
            headers=_headers(),
            json=payload,
            timeout=30.0
        )
        if response.status_code != 200:
            raise ValueError(f"ElevenLabs call failed ({response.status_code}): {response.text}")
        return response.json()


async def get_conversation(conversation_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ELEVENLABS_BASE}/convai/conversations/{conversation_id}",
            headers=_headers(),
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

async def get_conversation_audio(conversation_id: str) -> bytes:
    """
    Fetch the audio recording of a conversation from ElevenLabs.
    Returns raw MP3 bytes.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ELEVENLABS_BASE}/convai/conversations/{conversation_id}/audio",
            headers=_headers(),
            timeout=60.0
        )
        response.raise_for_status()
        return response.content

async def list_conversations(agent_id: str, page_size: int = 30) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ELEVENLABS_BASE}/convai/conversations",
            headers=_headers(),
            params={"agent_id": agent_id, "page_size": page_size},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


# ─── TTS ──────────────────────────────────────────────────────────────────────

async def text_to_speech(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """Convert text to speech. Works on free tier."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}",
            headers=_headers(),
            json={
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            },
            timeout=60.0
        )
        response.raise_for_status()
        return response.content


# ─── Voices ───────────────────────────────────────────────────────────────────

async def list_voices() -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ELEVENLABS_BASE}/voices",
            headers=_headers(),
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


# ─── Prompt Builder ───────────────────────────────────────────────────────────

def build_real_estate_system_prompt(
    developer_name: str,
    project_name: str,
    project_location: str,
    developer_rera: Optional[str] = None
) -> str:
    """Generate system prompt. Knowledge docs will be appended by campaign creator."""
    return f"""You are a professional real estate consultant calling on behalf of {developer_name}.
Your goal is to inform potential buyers about {project_name}, located in {project_location}.

INSTRUCTIONS:
1. Be warm, professional, and conversational. Never be pushy or aggressive.
2. Answer ALL questions about the project ONLY from the PROJECT KNOWLEDGE BASE section below.
3. If asked about pricing, unit types, amenities, possession dates, or RERA details - answer directly from the knowledge base.
4. If you don't have specific information, say "I'll have our team get back to you with those details."
5. Gauge buyer interest throughout the call.
6. If the prospect shows interest, encourage them to schedule a site visit.
7. Always mention the RERA registration number ({developer_rera or 'available on request'}) for credibility.
8. Keep calls concise but informative - aim for 3-5 minutes.
9. End the call politely regardless of their interest level.

GOAL: Identify genuinely interested buyers and encourage site visits.

DO NOT: Make false promises, share pricing not in the documents, or pressure prospects."""


# ─── Transcript Analysis ──────────────────────────────────────────────────────

def analyze_transcript_for_intent(transcript: str) -> dict:
    t = transcript.lower()

    # Site visit — highest priority, checked first
    site_visit_kw = [
        "visit", "site visit", "come see", "show me", "want to see",
        "schedule", "appointment", "when can i", "can i visit",
        "show flat", "show apartment", "want to come", "come tomorrow",
        "come this week", "book a visit", "site tour"
    ]

    # Not interested — checked before interested to avoid false positives
    # !! REMOVED bare "no" — it matched "know", "noted", "now", "location" etc.
    not_interested_kw = [
        "not interested", "no thanks", "don't need", "already bought",
        "not looking", "remove me", "don't call", "do not call",
        "no thank you", "not right now", "not at the moment",
        "already have", "no interest", "please don't", "stop calling",
        "don't want", "no need"
    ]

    # Callback
    callback_kw = [
        "call back", "call later", "call me later", "busy right now",
        "not a good time", "call tomorrow", "call next week",
        "in a meeting", "can't talk", "call me back"
    ]

    # Interested — broad, covers natural conversation responses
    interested_kw = [
        "interested", "tell me more", "sounds good", "sounds great",
        "want to know", "like to know", "please tell",
        "price", "pricing", "how much", "cost", "rate", "charges",
        "floor plan", "floor plans", "layout", "configuration", "bhk",
        "brochure", "details", "more details", "more information",
        "available", "availability", "possession", "handover",
        "amenities", "location", "size", "sqft", "square feet",
        "rera", "loan", "emi", "bank", "booking amount", "down payment",
        "payment plan", "installment",
        "yes", "yeah", "sure", "okay", "ok", "go ahead", "please",
        "i see", "i understand", "good", "great", "nice", "wow",
        "really", "tell me", "what about", "how about",
        "can you send", "please send", "whatsapp", "send me",
        "share the", "send the"
    ]

    if any(k in t for k in site_visit_kw):
        return {"outcome": "site_visit_requested", "interest_level": 5}
    elif any(k in t for k in not_interested_kw):
        return {"outcome": "not_interested", "interest_level": 1}
    elif any(k in t for k in callback_kw):
        return {"outcome": "callback_requested", "interest_level": 3}
    elif any(k in t for k in interested_kw):
        return {"outcome": "interested", "interest_level": 4}
    else:
        return {"outcome": "unknown", "interest_level": 2}
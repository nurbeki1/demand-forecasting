import os
import json
import logging
from typing import List, Dict, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── OpenAI (жауап жазу) ────────────────────────────────────────────────────
_openai_client = None
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if _OPENAI_API_KEY:
    try:
        _openai_client = OpenAI(api_key=_OPENAI_API_KEY)
        logger.info("[LLM] OpenAI client: ON")
    except Exception as e:
        logger.warning(f"[LLM] OpenAI init failed: {e}")
else:
    logger.warning("[LLM] OPENAI_API_KEY not set — OpenAI client disabled")

# ─── Gemini (контекст бақылаушы) ────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_gemini_client = None

if GEMINI_API_KEY:
    try:
        from google import genai as _genai
        _gemini_client = _genai.Client(api_key=GEMINI_API_KEY)
        logger.info("[LLM] Gemini context supervisor: ON (gemini-2.0-flash)")
    except Exception as e:
        logger.warning(f"[LLM] Gemini init failed: {e}")
        _gemini_client = None
else:
    logger.info("[LLM] Gemini context supervisor: OFF (no GEMINI_API_KEY)")


# ─── Gemini: контекстті шығару ───────────────────────────────────────────────

def extract_context_with_gemini(
    history: List[Dict[str, str]],
    current_message: str,
) -> Dict[str, Any]:
    """
    Gemini бүкіл чат тарихын талдайды және контекстті JSON ретінде қайтарады.

    Returns:
        {
          "current_product": "Samsung Galaxy S20 FE",
          "key_facts": "Пайдаланушы Қазақстанда сатқысы келеді",
          "is_followup": true,
          "corrected_query": "Samsung Galaxy S20 FE Қазақстан қалалары анализ"
        }
    """
    if not _gemini_client or not history:
        return {}

    try:
        # Тарихты мәтін форматына аудар
        history_text = ""
        for msg in history[-20:]:  # соңғы 20 хабар
            role = "Пайдаланушы" if msg.get("role") == "user" else "Жүйе"
            content = str(msg.get("content", ""))[:500]
            history_text += f"[{role}]: {content}\n"

        prompt = f"""Сен AI чат жүйесінің контекст бақылаушысысың.
Чат тарихын талдап, соңғы сұранымның нені білдіретінін анықта.

Чат тарихы:
{history_text}

Соңғы сұраным: "{current_message}"

Тек JSON форматында қайтар (түсіндірме жазба):
{{
  "current_product": "нақты өнім атауы немесе null",
  "key_facts": "контекстен маңызды фактілер (1-2 сөйлем)",
  "is_followup": true немесе false,
  "corrected_query": "нақтыланған сұраным (өнім аты + мақсат)"
}}"""

        response = _gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        text = response.text.strip()
        # JSON-ды markdown блогынан тазалау
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        result = json.loads(text)
        logger.info(f"[Gemini] Context extracted: product={result.get('current_product')}, followup={result.get('is_followup')}")
        return result

    except Exception as e:
        logger.warning(f"[Gemini] Context extraction failed: {e}")
        return {}


def _inject_context(system_prompt: str, ctx: Dict[str, Any]) -> str:
    """Gemini контекстін system prompt-қа қосу."""
    if not ctx:
        return system_prompt

    parts = []
    if ctx.get("current_product"):
        parts.append(f"Талқыланып жатқан өнім: {ctx['current_product']}")
    if ctx.get("key_facts"):
        parts.append(f"Контекст: {ctx['key_facts']}")
    if ctx.get("is_followup"):
        parts.append("Бұл алдыңғы сұранымның жалғасы.")

    if parts:
        context_block = "\n\n[CONTEXT SUPERVISOR]\n" + "\n".join(parts) + "\n[/CONTEXT SUPERVISOR]"
        return system_prompt + context_block

    return system_prompt


# ─── Негізгі функциялар ──────────────────────────────────────────────────────

def ask_llm(
    system_prompt: str,
    user_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    OpenAI GPT арқылы жауап береді.
    Gemini API кілті болса — алдымен контекстті шығарып, system prompt-қа қосады.
    """
    # Gemini бар болса → контекстті шығар, system prompt-ты байыт
    if _gemini_client and history and len(history) >= 2:
        ctx = extract_context_with_gemini(history, user_prompt)
        system_prompt = _inject_context(system_prompt, ctx)

    return _ask_openai(system_prompt, user_prompt, history)


def ask_llm_with_context(
    system_prompt: str,
    user_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """ask_llm-нің псевдонимі — GPT + Gemini контекст бақылаушысы."""
    return ask_llm(system_prompt, user_prompt, history)


def _ask_openai(
    system_prompt: str,
    user_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """OpenAI GPT-4o-mini шақыру (өзгеріссіз)."""
    if not _openai_client:
        raise RuntimeError("OPENAI_API_KEY is not configured on this server.")

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for msg in history[-10:]:
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"][:1500]})

    messages.append({"role": "user", "content": user_prompt})

    response = _openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content

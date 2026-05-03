import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_llm(
    system_prompt: str,
    user_prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Call OpenAI LLM with optional conversation history.

    Args:
        system_prompt: System instructions
        user_prompt: Current user message
        history: Optional list of {"role": "user"/"assistant", "content": "..."} messages
                 representing prior turns. Injected between system and current message.

    Returns:
        Assistant response string
    """
    messages = [{"role": "system", "content": system_prompt}]

    if history:
        # Keep last 10 turns to stay within context window
        for msg in history[-10:]:
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"][:1500]})

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content
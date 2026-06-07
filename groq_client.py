import streamlit as st
from groq import Groq


def get_client() -> Groq:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("GROQ_API_KEY not found. Add it to Streamlit secrets.")
        st.stop()
    return Groq(api_key=api_key)


def ask_groq(client: Groq, prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ABS RCA Vyšetřovatel", page_icon="🕵️")
st.title("🕵️ AI Asistent pro analýzu kořenových příčin (ABS)")

# Postranní panel pro vložení klíče
with st.sidebar:
    st.header("Nastavení")
    api_key = st.text_input("Vložte Gemini API klíč:", type="password")
    if st.button("Vymazat historii chatu"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

if not api_key:
    st.warning("👈 Pro spuštění vložte do postranního panelu svůj Gemini API klíč.")
    st.stop()

# Aktivace umělé inteligence
genai.configure(api_key=api_key)

# Instrukce pro AI (znalostní báze)
system_instruction = """
Jsi expertní vyšetřovatel BOZP a skoronehod. Tvým úkolem je analyzovat incidenty a určit kořenovou příčinu (Root Cause) striktně podle metodiky ABS.
Ptej se uživatele na detaily incidentu. Pokud je popis stručný, polož max 3 doplňující otázky.
Vždy komunikuj česky, ale kategorie ABS uváděj v angličtině (např. Procedure Issue, Human Factors Issue, Design Issue...).
Jakmile máš jasno, vypiš finální verdikt: Shrnutí, Direct Cause, ABS Intermediate Cause a ABS Root Cause.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# Paměť konverzace
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Dobrý den. Jsem váš RCA asistent. Popište mi prosím incident, který chcete analyzovat."}]
    
if "chat" not in st.session_state or st.session_state.chat is None:
    st.session_state.chat = model.start_chat(history=[])

# Zobrazení historie chatu
for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg["content"])

# Uživatelské okénko pro psaní
if prompt := st.chat_input("Napište popis incidentu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*(Přemýšlím...)*")
        try:
            response = st.session_state.chat.send_message(prompt)
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
        except Exception as e:
            message_placeholder.error("Chyba API. Zkontrolujte, zda je API klíč správný.")

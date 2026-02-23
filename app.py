import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ABS RCA Vyšetřovatel", page_icon="🕵️")
st.title("🕵️ AI Asistent pro analýzu kořenových příčin (ABS)")

# Postranní panel
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

# Konfigurace
genai.configure(api_key=api_key)

# 1. AUTOMATICKÉ VYHLEDÁNÍ POVOLENÉHO MODELU
if "spravny_model" not in st.session_state:
    st.session_state.spravny_model = None
    try:
        dostupne_modely = []
        # Aplikace si sama vyžádá seznam povolených modelů od Googlu
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                dostupne_modely.append(m.name)
        
        if dostupne_modely:
            # Ze seznamu vybere ten nejlepší (ideálně s označením flash nebo pro)
            vybrany = dostupne_modely[0] 
            for m in dostupne_modely:
                if "flash" in m:
                    vybrany = m
                    break
                elif "pro" in m:
                    vybrany = m
            st.session_state.spravny_model = vybrany
        else:
            st.error("Tento API klíč nemá povolené žádné textové modely.")
            st.stop()
    except Exception as e:
        st.error(f"Nepodařilo se ověřit dostupné modely: {e}")
        st.stop()

# Ukáže vám, jaký model aplikace u Googlu našla a použila
st.success(f"✅ Úspěšně napojeno na model: **{st.session_state.spravny_model}**")

# 2. NASTAVENÍ ASISTENTA
system_instruction = """
Jsi expertní vyšetřovatel BOZP a skoronehod. Tvým úkolem je analyzovat incidenty a určit kořenovou příčinu (Root Cause) striktně podle metodiky ABS.
Ptej se uživatele na detaily incidentu. Pokud je popis stručný, polož max 3 doplňující otázky.
Vždy komunikuj česky, ale kategorie ABS uváděj v angličtině (např. Procedure Issue, Human Factors Issue, Design Issue...).
Jakmile máš jasno, vypiš finální verdikt: Shrnutí, Direct Cause, ABS Intermediate Cause a ABS Root Cause.
"""

# Založení modelu
try:
    model = genai.GenerativeModel(
        model_name=st.session_state.spravny_model,
        system_instruction=system_instruction
    )
except:
    # Záloha pro případ, že vybraný model neumí pokročilé instrukce
    model = genai.GenerativeModel(model_name=st.session_state.spravny_model)

# 3. PAMĚŤ A CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Dobrý den. Jsem váš RCA asistent. Popište mi prosím incident, který chcete analyzovat."}]
    
if "chat" not in st.session_state or st.session_state.chat is None:
    st.session_state.chat = model.start_chat(history=[])

for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg["content"])

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
            message_placeholder.error(f"Chyba při odpovídání: {e}")

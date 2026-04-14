import streamlit as st
import pandas as pd
import os
from twilio.rest import Client

# CONFIG
st.set_page_config(
    page_title="Mandelas Hair Studio",
    page_icon="💈",
    layout="centered"
)

# 🎨 ESTILO PREMIUM
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.main {
    background-color: #0e1117;
    color: white;
}

/* Botões normais */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    padding: 12px;
    font-weight: bold;
    background-color: #1f2937;
    color: white;
}

/* Botão principal */
div.stButton > button:first-child {
    background-color: #f5c542;
    color: black;
}

/* Inputs */
.stTextInput input {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# LOGO
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.jpg", width=250)

st.markdown("<h2 style='text-align:center;'>Mandelas Hair Studio</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Reserva o teu corte em segundos</p>", unsafe_allow_html=True)

st.markdown("---")

# TWILIO
account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
twilio_number = st.secrets["TWILIO_WHATSAPP_NUMBER"]

client = Client(account_sid, auth_token)

def enviar_whatsapp(numero, mensagem):
    try:
        client.messages.create(
            body=mensagem,
            from_=twilio_number,
            to=f"whatsapp:{numero}"
        )
    except:
        pass

def formatar_numero(numero):
    numero = numero.replace(" ", "")
    if not numero.startswith("+351"):
        numero = "+351" + numero
    return numero

# CSV
FILE = "dados.csv"
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Nome","Telefone","Data","Hora","Serviço"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# INPUTS
st.subheader("📅 Nova Marcação")

nome = st.text_input("Nome")
telefone = st.text_input("Telefone")
data = st.date_input("Escolhe o dia")

# HORÁRIOS
st.subheader("⏰ Horários disponíveis")

horarios = [
    "09:00","09:30","10:00","10:30",
    "11:00","11:30","12:00",
    "14:00","14:30","15:00","15:30",
    "16:00","16:30","17:00","17:30"
]

ocupados = df[df["Data"] == str(data)]["Hora"].tolist()

hora_escolhida = st.session_state.get("hora", None)

cols = st.columns(4)

for i, h in enumerate(horarios):
    if h in ocupados:
        cols[i % 4].button(f"{h} ❌", disabled=True)
    else:
        if cols[i % 4].button(h):
            st.session_state["hora"] = h
            hora_escolhida = h

# MOSTRAR ESCOLHA
if hora_escolhida:
    st.success(f"⏰ Hora selecionada: {hora_escolhida}")

servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte + Barba"])

# BOTÃO PRINCIPAL
if st.button("💈 Confirmar Marcação"):

    if nome and telefone and hora_escolhida:

        telefone = formatar_numero(telefone)

        novo = pd.DataFrame([{
            "Nome": nome,
            "Telefone": telefone,
            "Data": str(data),
            "Hora": hora_escolhida,
            "Serviço": servico
        }])

        df = pd.concat([df, novo], ignore_index=True)
        df.to_csv(FILE, index=False)

        mensagem = f"""
💈 Mandelas Hair Studio

Olá {nome}!

A tua marcação está confirmada:

📅 {data}
⏰ {hora_escolhida}
✂️ {servico}

Até breve 🔥
"""

        enviar_whatsapp(telefone, mensagem)

        st.success("✅ Marcação confirmada!")

        # limpar hora
        st.session_state["hora"] = None

    else:
        st.error("Preenche tudo e escolhe uma hora")

# AGENDA
st.markdown("---")
st.subheader("📅 Agenda")

st.dataframe(df.sort_values(["Data","Hora"]))

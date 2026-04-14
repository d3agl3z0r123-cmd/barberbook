import streamlit as st
import pandas as pd
from datetime import datetime
from twilio.rest import Client
import os

# CONFIG
st.set_page_config(page_title="BarberBook", page_icon="💈")

st.title("💈 BarberBook")
st.subheader("📅 Marcar Corte")

# TWILIO CONFIG
account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
twilio_number = st.secrets["TWILIO_WHATSAPP_NUMBER"]

client = Client(account_sid, auth_token)

# FUNÇÃO PARA ENVIAR WHATSAPP
def enviar_whatsapp(numero, mensagem):
    try:
        client.messages.create(
            body=mensagem,
            from_=twilio_number,
            to=f"whatsapp:{numero}"
        )
        return True
    except Exception as e:
        st.warning(f"Agendamento guardado, mas erro no WhatsApp: {e}")
        return False

# FICHEIRO CSV
FILE = "dados.csv"

# SE NÃO EXISTIR, CRIAR
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Nome", "Telefone", "Data", "Hora", "Serviço"])
    df.to_csv(FILE, index=False)

# FORMULÁRIO
with st.form("agendamento"):
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone (+351...)")
    data = st.date_input("Data")
    hora = st.time_input("Hora")

    servico = st.selectbox(
        "Serviço",
        ["Corte", "Barba", "Corte + Barba"]
    )

    submitted = st.form_submit_button("Confirmar Marcação")

# AO SUBMETER
if submitted:
    if nome and telefone:
        # GUARDAR DADOS
        novo = pd.DataFrame([{
            "Nome": nome,
            "Telefone": telefone,
            "Data": data,
            "Hora": hora,
            "Serviço": servico
        }])

        df = pd.read_csv(FILE)
        df = pd.concat([df, novo], ignore_index=True)
        df.to_csv(FILE, index=False)

        # MENSAGEM WHATSAPP
        mensagem = f"""
💈 BarberBook

Olá {nome}!
A tua marcação está confirmada:

📅 Data: {data}
⏰ Hora: {hora}
✂️ Serviço: {servico}

Obrigado! 🙌
"""

        sucesso = enviar_whatsapp(telefone, mensagem)

        if sucesso:
            st.success("✅ Marcação feita e WhatsApp enviado!")
        else:
            st.warning("⚠️ Marcação guardada, mas erro no envio do WhatsApp.")

    else:
        st.error("Preenche todos os campos!")

# MOSTRAR AGENDAMENTOS
st.subheader("📋 Agendamentos")

df = pd.read_csv(FILE)

if not df.empty:
    st.dataframe(df)
else:
    st.info("Ainda não há marcações.")

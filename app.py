import streamlit as st
import pandas as pd
import os
from twilio.rest import Client

# CONFIG
st.set_page_config(page_title="BarberBook", page_icon="💈")

st.title("💈 BarberBook")
st.subheader("📅 Marcar Corte")

# TWILIO
account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
twilio_number = st.secrets["TWILIO_WHATSAPP_NUMBER"]

client = Client(account_sid, auth_token)

# FUNÇÃO WHATSAPP
def enviar_whatsapp(numero, mensagem):
    try:
        client.messages.create(
            body=mensagem,
            from_=twilio_number,
            to=f"whatsapp:{numero}"
        )
        return True
    except Exception as e:
        st.warning(f"Erro no WhatsApp: {e}")
        return False

# CSV
FILE = "dados.csv"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Nome", "Telefone", "Data", "Hora", "Serviço"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# FORMULÁRIO
with st.form("agendamento"):

    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone (+351...)")

    data = st.date_input("Data")

    # HORÁRIOS BASE
    horarios_base = [
        "09:00", "09:30", "10:00", "10:30",
        "11:00", "11:30", "12:00",
        "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30"
    ]

    # OCUPADOS
    ocupados = df[df["Data"] == str(data)]["Hora"].astype(str).tolist()

    # DISPONÍVEIS
    disponiveis = [h for h in horarios_base if h not in ocupados]

    if disponiveis:
        hora = st.selectbox("Hora", disponiveis)
    else:
        st.warning("Sem horários disponíveis neste dia")
        hora = None

    servico = st.selectbox(
        "Serviço",
        ["Corte", "Barba", "Corte + Barba"]
    )

    submitted = st.form_submit_button("Confirmar Marcação")

# GUARDAR
if submitted:
    if nome and telefone and hora:

        novo = pd.DataFrame([{
            "Nome": nome,
            "Telefone": telefone,
            "Data": str(data),
            "Hora": hora,
            "Serviço": servico
        }])

        df = pd.concat([df, novo], ignore_index=True)
        df.to_csv(FILE, index=False)

        mensagem = f"""
💈 Barbearia

Olá {nome}!

A tua marcação está confirmada:

📅 {data}
⏰ {hora}
✂️ {servico}

Até breve 👌
"""

        sucesso = enviar_whatsapp(telefone, mensagem)

        if sucesso:
            st.success("✅ Marcação feita e WhatsApp enviado!")
        else:
            st.warning("Marcação guardada, mas erro no WhatsApp")

    else:
        st.error("Preenche todos os campos")

# PAINEL BARBEIRO
st.subheader("📅 Agenda do Dia")

filtro_data = st.date_input("Ver agenda de:")

agenda = df[df["Data"] == str(filtro_data)]

if not agenda.empty:
    st.dataframe(agenda.sort_values("Hora"))
else:
    st.info("Sem marcações neste dia")

# LISTA COMPLETA
st.subheader("📋 Todos os Agendamentos")

if not df.empty:
    st.dataframe(df)
else:
    st.info("Sem dados ainda")
else:
    st.info("Ainda não há marcações.")

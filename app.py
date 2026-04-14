import streamlit as st
import pandas as pd
import os
from twilio.rest import Client

# CONFIG
st.set_page_config(
    page_title="Mandelas Hair Studio Barbershop",
    page_icon="💈",
    layout="centered"
)

# 🎨 ESTILO PROFISSIONAL
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
    }
    .main {
        background-color: #0e1117;
        color: white;
    }
    .stButton>button {
        background-color: #f5c542;
        color: black;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px;
        width: 100%;
    }
    .stTextInput input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 🖼️ LOGO (JPEG)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.jpg", width=300)

st.markdown("<h2 style='text-align:center;'>Mandelas Hair Studio Barbershop</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Estilo • Precisão • Confiança</p>", unsafe_allow_html=True)

st.markdown("---")

# TWILIO
account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
twilio_number = st.secrets["TWILIO_WHATSAPP_NUMBER"]

client = Client(account_sid, auth_token)

# WHATSAPP
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

# FORMATAR Nº
def formatar_numero(numero):
    numero = numero.replace(" ", "")
    if not numero.startswith("+351"):
        numero = "+351" + numero
    return numero

# CSV
FILE = "dados.csv"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Nome", "Telefone", "Data", "Hora", "Serviço"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# FORMULÁRIO
st.subheader("📅 Marcar Corte")

with st.form("agendamento"):

    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone (ex: 925349904)")
    data = st.date_input("Data")

    horarios_base = [
        "09:00","09:30","10:00","10:30",
        "11:00","11:30","12:00",
        "14:00","14:30","15:00","15:30",
        "16:00","16:30","17:00","17:30"
    ]

    ocupados = df[df["Data"] == str(data)]["Hora"].astype(str).tolist()
    disponiveis = [h for h in horarios_base if h not in ocupados]

    if len(disponiveis) > 0:
        hora = st.selectbox("Hora", disponiveis)
    else:
        st.warning("Sem horários disponíveis")
        hora = None

    servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte + Barba"])

    submitted = st.form_submit_button("Confirmar Marcação")

# GUARDAR
if submitted:

    if nome and telefone and hora:

        telefone_formatado = formatar_numero(telefone)

        novo = pd.DataFrame([{
            "Nome": nome,
            "Telefone": telefone_formatado,
            "Data": str(data),
            "Hora": hora,
            "Serviço": servico
        }])

        df = pd.concat([df, novo], ignore_index=True)
        df.to_csv(FILE, index=False)

        mensagem = f"""
💈 Mandelas Hair Studio

Olá {nome}!

A tua marcação está confirmada:

📅 {data}
⏰ {hora}
✂️ {servico}

Esperamos por ti 🔥
"""

        sucesso = enviar_whatsapp(telefone_formatado, mensagem)

        if sucesso:
            st.success("✅ Marcação confirmada e WhatsApp enviado!")
        else:
            st.warning("Marcação guardada, mas erro no WhatsApp")

    else:
        st.error("Preenche todos os campos")

# AGENDA
st.markdown("---")
st.subheader("📅 Agenda")

filtro_data = st.date_input("Ver agenda de:")

agenda = df[df["Data"] == str(filtro_data)]

if len(agenda) > 0:
    st.dataframe(agenda.sort_values("Hora"))
else:
    st.info("Sem marcações")

# TODOS
st.markdown("---")
st.subheader("📋 Todos os Agendamentos")

st.dataframe(df)

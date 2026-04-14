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

# PASSWORD BARBEIRO
PASSWORD = "1234"  # 🔥 MUDA ISTO!

# ESTILO
st.markdown("""
<style>
.stButton>button {
    width: 100%;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

# LOGO
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.jpg", width=250)

st.markdown("## 💈 Mandelas Hair Studio")
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
    if not numero.startswith("+351"):
        numero = "+351" + numero
    return numero

# CSV
FILE = "dados.csv"
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Nome","Telefone","Data","Hora","Serviço"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# MENU
modo = st.radio("Escolhe:", ["Cliente", "Barbeiro"])

# ================= CLIENTE =================
if modo == "Cliente":

    st.subheader("📅 Nova Marcação")

    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    data = st.date_input("Data")

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

    if hora_escolhida:
        st.success(f"Hora: {hora_escolhida}")

    servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte + Barba"])

    if st.button("Confirmar"):

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
Marcaçao confirmada:

📅 {data}
⏰ {hora_escolhida}
✂️ {servico}
"""

            enviar_whatsapp(telefone, mensagem)

            st.success("✅ Marcado!")

            st.session_state["hora"] = None

        else:
            st.error("Preenche tudo")

# ================= BARBEIRO =================
else:

    st.subheader("🔐 Área do Barbeiro")

    password_input = st.text_input("Password", type="password")

    if password_input == PASSWORD:

        st.success("Acesso autorizado")

        st.subheader("📅 Agenda")

        st.dataframe(df.sort_values(["Data","Hora"]))

    elif password_input:
        st.error("Password errada")

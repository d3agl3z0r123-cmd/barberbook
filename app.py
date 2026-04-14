import streamlit as st
import pandas as pd
import os
import urllib.parse

# CONFIG
st.set_page_config(page_title="Mandelas Hair Studio", page_icon="💈")

# PREÇOS
PREÇOS = {
    "Corte": 10,
    "Barba": 5,
    "Corte + Barba": 15
}

# FUNÇÃO WHATSAPP DIRETO
def abrir_whatsapp(numero, mensagem):
    numero = numero.replace("+", "")
    mensagem = urllib.parse.quote(mensagem)
    link = f"https://wa.me/{numero}?text={mensagem}"
    return link

def formatar_numero(numero):
    numero = numero.replace(" ", "")
    if not numero.startswith("+351"):
        numero = "+351" + numero
    return numero

# CSV
FILE = "dados.csv"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["Nome","Telefone","Data","Hora","Serviço","Barbeiro"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# LOGO
st.image("logo.jpg", width=250)
st.title("💈 Mandelas Hair Studio")

modo = st.radio("Escolhe:", ["Cliente", "Barbeiro"])

# ================= CLIENTE =================
if modo == "Cliente":

    st.subheader("📅 Nova Marcação")

    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")

    data = st.date_input("Data")

    barbeiro = st.selectbox("Escolhe o barbeiro", ["Diogo", "Delcio"])

    horarios = [
        "09:00","09:30","10:00","10:30",
        "11:00","11:30","12:00",
        "14:00","14:30","15:00","15:30",
        "16:00","16:30","17:00","17:30"
    ]

    ocupados = df[(df["Data"] == str(data)) & (df["Barbeiro"] == barbeiro)]["Hora"].tolist()

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
        st.success(f"⏰ Hora selecionada: {hora_escolhida}")

    servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte + Barba"])

    if st.button("💈 Confirmar Marcação"):

        if nome and telefone and hora_escolhida:

            telefone = formatar_numero(telefone)

            novo = pd.DataFrame([{
                "Nome": nome,
                "Telefone": telefone,
                "Data": str(data),
                "Hora": hora_escolhida,
                "Serviço": servico,
                "Barbeiro": barbeiro
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
👤 {barbeiro}

Até breve 🔥
"""

            link = abrir_whatsapp(telefone, mensagem)

            st.success("✅ Marcação feita!")

            st.markdown(f"👉 [📲 Confirmar no WhatsApp]({link})")

            st.session_state["hora"] = None

        else:
            st.error("Preenche todos os campos")

# ================= BARBEIRO =================
else:

    USERS = {
        "Diogo": "1234",
        "Delcio": "1234"
    }

    user = st.selectbox("Barbeiro", ["Diogo", "Delcio"])
    password = st.text_input("Password", type="password")

    if USERS.get(user) == password:

        st.success(f"Bem-vindo {user}")

        df_user = df[df["Barbeiro"] == user]

        # DASHBOARD
        total = df_user["Serviço"].map(PREÇOS).sum()
        hoje = df_user[df_user["Data"] == str(pd.to_datetime("today").date())]["Serviço"].map(PREÇOS).sum()

        col1, col2 = st.columns(2)
        col1.metric("💰 Total", f"{total}€")
        col2.metric("📅 Hoje", f"{hoje}€")

        st.subheader("📅 Agenda")

        for i, row in df_user.iterrows():

            col1, col2, col3, col4 = st.columns([2,2,2,1])

            col1.write(row["Data"])
            col2.write(row["Hora"])
            col3.write(row["Nome"])

            if col4.button("❌", key=i):
                df = df.drop(i)
                df.to_csv(FILE, index=False)
                st.rerun()

    elif password:
        st.error("Password errada")

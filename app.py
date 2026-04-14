import streamlit as st
import pandas as pd
from twilio.rest import Client

# 🔑 TWILIO CONFIG
account_sid = "ACf8bcfa107ea60ff92a1aa0f9847dfb27"
auth_token = st.secrets["85764297dea3b9a7a2754275629c6fef"]
twilio_number = "+17406699179"

client = Client(account_sid, auth_token)

# 📂 Ficheiro CSV
FILE = "dados.csv"

# Criar ficheiro se não existir OU atualizar colunas
try:
    df = pd.read_csv(FILE)
except:
    df = pd.DataFrame(columns=["Nome", "Telefone", "Data", "Hora", "Serviço"])
    df.to_csv(FILE, index=False)

# Garantir colunas corretas (corrige dados antigos)
colunas = ["Nome", "Telefone", "Data", "Hora", "Serviço"]
for col in colunas:
    if col not in df.columns:
        df[col] = ""

df = df[colunas]

# 🎨 APP
st.set_page_config(page_title="BarberBook", page_icon="💈")
st.title("💈 BarberBook")
st.subheader("📅 Marcar Corte")

# 📌 FORMULÁRIO
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

    if submitted:
        if nome == "" or telefone == "":
            st.warning("Preenche todos os campos!")
        else:
            novo = pd.DataFrame([[nome, telefone, data, hora, servico]],
                                columns=colunas)

            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(FILE, index=False)

            # 📩 ENVIAR SMS
            try:
                mensagem = f"Olá {nome}, o seu agendamento para {servico} está marcado para {data} às {hora} 💈"

                client.messages.create(
                    body=mensagem,
                    from_=twilio_number,
                    to=telefone
                )

                st.success("✅ Agendamento guardado e SMS enviado!")

            except Exception as e:
                st.warning("⚠️ Agendamento guardado, mas erro no SMS")
                st.text(e)

# 📋 LISTA
st.subheader("📋 Agendamentos")
st.dataframe(df)

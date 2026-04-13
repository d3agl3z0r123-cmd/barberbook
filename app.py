import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="BarberBook", layout="wide")

st.title("💈 BarberBook")

FILE = "dados.csv"

barbeiros = ["Diogo (Martinez)", "Delcio Mandelas"]

# gerar horários
def gerar_horarios():
    horarios = []
    
    hora = datetime.strptime("09:00", "%H:%M")
    while hora < datetime.strptime("13:00", "%H:%M"):
        horarios.append(hora.strftime("%H:%M"))
        hora += pd.Timedelta(minutes=30)

    hora = datetime.strptime("14:00", "%H:%M")
    while hora < datetime.strptime("19:00", "%H:%M"):
        horarios.append(hora.strftime("%H:%M"))
        hora += pd.Timedelta(minutes=30)

    return horarios

horarios = gerar_horarios()

# carregar dados
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Barbeiro", "Nome", "Data", "Hora"])

# -------------------------
# MENU
# -------------------------
menu = st.sidebar.radio("Menu", ["Cliente", "Barbeiro"])

# =========================
# CLIENTE
# =========================
if menu == "Cliente":
    st.header("📲 Marcar Corte")

    barbeiro = st.selectbox("Escolhe o barbeiro", barbeiros)
    nome = st.text_input("O teu nome")
    data = st.date_input("Escolhe a data")

    ocupados = df[(df["Barbeiro"] == barbeiro) & (df["Data"] == str(data))]["Hora"].tolist()
    disponiveis = [h for h in horarios if h not in ocupados]

    if len(disponiveis) == 0:
        st.error("Sem horários disponíveis neste dia")
    else:
        hora = st.selectbox("Escolhe a hora", disponiveis)

        if st.button("Confirmar Marcação"):
            novo = pd.DataFrame([{
                "Barbeiro": barbeiro,
                "Nome": nome,
                "Data": str(data),
                "Hora": hora
            }])

            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(FILE, index=False)

            st.success(f"✅ Marcação confirmada para {hora}")

# =========================
# BARBEIRO
# =========================
if menu == "Barbeiro":
    st.header("📅 Gestão da Agenda")

    filtro_barbeiro = st.selectbox("Selecionar Barbeiro", barbeiros)
    filtro_data = st.date_input("Selecionar Data", datetime.today())

    # 🔔 ALERTA 4 HORAS ANTES
    agora = datetime.now()
    daqui_4h = agora + timedelta(hours=4)

    st.subheader("🔔 Próximos cortes (até 4h)")

    for i, row in df.iterrows():
        data_hora_str = f"{row['Data']} {row['Hora']}"
        data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")

        if agora <= data_hora <= daqui_4h:
            st.warning(f"{row['Hora']} - {row['Nome']} ({row['Barbeiro']})")

    # agenda normal
    agenda = df[
        (df["Barbeiro"] == filtro_barbeiro) &
        (df["Data"] == str(filtro_data))
    ]

    for h in horarios:
        slot = agenda[agenda["Hora"] == h]
        
        if not slot.empty:
            nome_cliente = slot.iloc[0]["Nome"]
            col1, col2 = st.columns([3,1])
            
            with col1:
                st.error(f"{h} - {nome_cliente}")
            
            with col2:
                pin = st.text_input(f"PIN {h}", type="password", key=f"pin_{h}")
                
                if st.button(f"Apagar {h}", key=f"btn_{h}"):

                    if filtro_barbeiro == "Diogo (Martinez)" and pin == "1111":
                        df = df.drop(slot.index)

                    elif filtro_barbeiro == "Delcio Mandelas" and pin == "2222":
                        df = df.drop(slot.index)

                    else:
                        st.error("PIN incorreto")
                        st.stop()

                    df.to_csv(FILE, index=False)
                    st.rerun()
        else:
            st.success(f"{h} - Livre")
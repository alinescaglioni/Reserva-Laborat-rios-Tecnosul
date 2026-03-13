import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
laboratorios_disponiveis = ["Laboratório de Informática 1", "Laboratório de Informática 2", "Laboratório de Química", "Laboratório de Física"]
horarios_inicio = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

st.set_page_config(page_title="Gestão de Laboratórios", layout="wide")
st.title("🧪 Sistema de Agendamento de Laboratórios")

# --- BANCO DE DADOS (CSV) ---
try:
    df_reservas = pd.read_csv("reservas_labs.csv")
except FileNotFoundError:
    df_reservas = pd.DataFrame(columns=["Laboratório", "Data", "Início", "Término", "Responsável"])

# --- ÁREA DE INPUT ---
st.subheader("Fazer Nova Reserva")
col1, col2, col3 = st.columns(3)

with col1:
    lab_selecionado = st.selectbox("Selecione o Laboratório", laboratorios_disponiveis)
    nome_responsavel = st.text_input("Seu Nome (Responsável)")

with col2:
    data_selecionada = st.date_input("Escolha a Data", min_value=datetime.today())
    hora_inicio_sel = st.selectbox("Horário de Início", horarios_inicio)

with col3:
    # Cálculo automático da hora de término (1 hora depois do início)
    hora_dt = datetime.strptime(hora_inicio_sel, "%H:%M")
    hora_termino_sugerida = (hora_dt + timedelta(hours=1)).strftime("%H:%M")
    hora_termino_sel = st.text_input("Horário de Término", value=hora_termino_sugerida)

if st.button("Confirmar Agendamento"):
    if nome_responsavel == "":
        st.error("Por favor, preencha o nome do responsável.")
    else:
        # VERIFICAÇÃO DE CONFLITO
        conflito = df_reservas[
            (df_reservas['Laboratório'] == lab_selecionado) & 
            (df_reservas['Data'] == str(data_selecionada)) & 
            (df_reservas['Início'] == hora_inicio_sel)
        ]
        
        if not conflito.empty:
            st.error(f"O {lab_selecionado} já está reservado para {hora_inicio_sel} nesta data.")
        else:
            nova_reserva = pd.DataFrame([[lab_selecionado, str(data_selecionada), hora_inicio_sel, hora_termino_sel, nome_responsavel]], 
                                       columns=["Laboratório", "Data", "Início", "Término", "Responsável"])
            df_reservas = pd.concat([df_reservas, nova_reserva], ignore_index=True)
            df_reservas.to_csv("reservas_labs.csv", index=False)
            st.success("Reserva realizada com sucesso!")
            st.balloons()
            st.rerun()

# --- TABELA DE AGENDAMENTOS (LISTA ABAIXO) ---
st.divider()
st.subheader("📅 Agendamentos Realizados")

if df_reservas.empty:
    st.info("Ainda não há reservas para exibir.")
else:
    # Ordenar a lista por data e hora de início
    df_lista = df_reservas.sort_values(by=["Data", "Início"])
    st.dataframe(df_lista, use_container_width=True)

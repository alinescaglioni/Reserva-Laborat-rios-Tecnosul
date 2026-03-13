import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DOS HORÁRIOS PERMITIDOS ---
horarios_disponiveis = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

st.title("Sistema de Agendamento Profissional")

# 1. ENTRADA DE DADOS
data_selecionada = st.date_input("Escolha a data", min_value=datetime.today())
horario_selecionado = st.selectbox("Escolha o horário", horarios_disponiveis)
nome_cliente = st.text_input("Seu nome completo")

# Simulação de carregamento de dados (Substitua pela sua lógica de leitura de arquivo/planilha)
# Se você estiver usando um CSV, o código abaixo verifica se já existe o agendamento
try:
    df_reservas = pd.read_csv("reservas.csv")
except FileNotFoundError:
    df_reservas = pd.DataFrame(columns=["Data", "Horário", "Cliente"])

if st.button("Confirmar Agendamento"):
    if nome_cliente == "":
        st.error("Por favor, preencha seu nome.")
    else:
        # 2. VERIFICAÇÃO DE DISPONIBILIDADE
        # Filtra se já existe uma linha com a mesma data e mesmo horário
        conflito = df_reservas[(df_reservas['Data'] == str(data_selecionada)) & 
                               (df_reservas['Horário'] == horario_selecionado)]
        
        if not conflito.empty:
            st.error(f"Sinto muito! O horário {horario_selecionado} no dia {data_selecionada} já está ocupado.")
        else:
            # 3. SALVAR NOVA RESERVA
            nova_reserva = pd.DataFrame([[str(data_selecionada), horario_selecionado, nome_cliente]], 
                                        columns=["Data", "Horário", "Cliente"])
            df_reservas = pd.concat([df_reservas, nova_reserva], ignore_index=True)
            df_reservas.to_csv("reservas.csv", index=False)
            
            st.success(f"Agendamento realizado com sucesso para {nome_cliente} às {horario_selecionado}!")
            st.balloons()

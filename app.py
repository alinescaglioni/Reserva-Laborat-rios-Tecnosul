import streamlit as st
import pandas as pd
import os
from datetime import time, datetime

# Configuração do Banco de Dados em CSV
ARQUIVO_BANCO = "reservas_tecnosul.csv"
LABS = ["Criar LAB (Espaço Maker)", "Laboratório MEDGEN (Biotecnologia)", "Laboratório de Ensaios Experimentais"]

def carregar_dados():
    # Definimos as colunas atualizadas
    colunas = ["Nome Completo", "Laboratório", "Data", "Início", "Término"]
    if os.path.exists(ARQUIVO_BANCO):
        df = pd.read_csv(ARQUIVO_BANCO)
        # Verifica se o CSV antigo tem as colunas novas, se não, reseta
        if "Início" not in df.columns:
            return pd.DataFrame(columns=colunas)
        return df
    return pd.DataFrame(columns=colunas)

def salvar_dados(df):
    df.to_csv(ARQUIVO_BANCO, index=False)

st.title("📍 Reserva de Laboratórios - Tecnosul")

# Interface de Agendamento
with st.expander("➕ Realizar Nova Reserva", expanded=True):
    with st.form("form_reserva", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        lab_selecionado = st.selectbox("Selecione o Laboratório", LABS)
        data = st.date_input("Data do Agendamento", min_value=datetime.today())
        
        col1, col2 = st.columns(2)
        with col1:
            h_inicio = st.time_input("Horário de Início", value=time(8, 0))
        with col2:
            h_termino = st.time_input("Horário de Término", value=time(9, 0))
        
        botao = st.form_submit_button("Confirmar Reserva")

    if botao:
        # Validações
        hora_abertura = time(8, 0)
        hora_fechamento = time(18, 0)

        if not (hora_abertura <= h_inicio <= hora_fechamento) or not (hora_abertura <= h_termino <= hora_fechamento):
            st.error("⚠️ As reservas só podem ser feitas entre as 08h e as 18h.")
        elif h_termino <= h_inicio:
            st.error("⚠️ O horário de término deve ser após o horário de início.")
        elif not nome:
            st.error("⚠️ Por favor, informe seu nome completo.")
        else:
            df_atual = carregar_dados()
            nova_reserva = pd.DataFrame([[
                nome, 
                lab_selecionado, 
                data.strftime("%d/%m/%Y"), 
                h_inicio.strftime("%H:%M"), 
                h_termino.strftime("%H:%M")
            ]], columns=df_atual.columns)
            
            df_final = pd.concat([df_atual, nova_reserva], ignore_index=True)
            salvar_dados(df_final)
            st.success(f"✅ Sucesso! {lab_selecionado} reservado para {nome}.")
            st.rerun()

# Exibição da Planilha
st.subheader("📋 Cronograma de Reservas")
df_lista = carregar_dados()
if not df_lista.empty:
    # Ordenar por data e hora de início
    st.dataframe(df_lista.sort_values(by=["Data", "Início"]), use_container_width=True)
else:
    st.info("Nenhuma reserva encontrada na planilha.")

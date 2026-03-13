import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
# Atualizado para os laboratórios do Pelotas Parque Tecnológico
laboratorios_ppt = [
    "Criar LAB", 
    "Laboratório de Validação (Produtos da Saúde)", 
    "Laboratório MEDGEN (Biotecnológia)"
]

horarios_inicio = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

st.set_page_config(page_title="PPT - Marcação de Labs", layout="wide", page_icon="🏢")

# Título solicitado
st.title("🏢 Marcação de Laboratórios do Pelotas Parque Tecnológico")

# --- BANCO DE DADOS (CSV) ---
try:
    df_reservas = pd.read_csv("reservas_ppt.csv")
except FileNotFoundError:
    df_reservas = pd.DataFrame(columns=["Laboratório", "Data", "Início", "Término", "Responsável"])

# --- ÁREA DE AGENDAMENTO ---
with st.expander("➕ Realizar Novo Agendamento", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        lab_selecionado = st.selectbox("Selecione o Laboratório", laboratorios_ppt)
        nome_responsavel = st.text_input("Nome do Responsável / Empresa")

    with col2:
        data_selecionada = st.date_input("Data do Uso", min_value=datetime.today())
        hora_inicio_sel = st.selectbox("Horário de Início", horarios_inicio)

    with col3:
        # Cálculo automático da hora de término (1 hora depois do início)
        hora_dt = datetime.strptime(hora_inicio_sel, "%H:%M")
        hora_termino_sugerida = (hora_dt + timedelta(hours=1)).strftime("%H:%M")
        hora_termino_sel = st.text_input("Horário de Término", value=hora_termino_sugerida)

    if st.button("Confirmar Agendamento"):
        if nome_responsavel == "":
            st.warning("Por favor, identifique o responsável pela reserva.")
        else:
            # VERIFICAÇÃO DE CONFLITO (Mesmo Lab + Mesma Data + Mesmo Horário)
            conflito = df_reservas[
                (df_reservas['Laboratório'] == lab_selecionado) & 
                (df_reservas['Data'] == str(data_selecionada)) & 
                (df_reservas['Início'] == hora_inicio_sel)
            ]
            
            if not conflito.empty:
                st.error(f"⚠️ Atenção: O {lab_selecionado} já possui reserva para este horário.")
            else:
                nova_reserva = pd.DataFrame([[lab_selecionado, str(data_selecionada), hora_inicio_sel, hora_termino_sel, nome_responsavel]], 
                                           columns=["Laboratório", "Data", "Início", "Término", "Responsável"])
                df_reservas = pd.concat([df_reservas, nova_reserva], ignore_index=True)
                df_reservas.to_csv("reservas_ppt.csv", index=False)
                st.success(f"Reserva no {lab_selecionado} confirmada!")
                st.balloons()
                st.rerun()

# --- QUADRO DE RESERVAS ---
st.markdown("---")
st.subheader("📅 Quadro de Ocupação")

if df_reservas.empty:
    st.info("Não há agendamentos registrados para os próximos dias.")
else:
    # Ordenar por data e horário para ficar organizado
    df_lista = df_reservas.sort_values(by=["Data", "Início"], ascending=True)
    
    # Exibe a tabela formatada
    st.dataframe(df_lista, use_container_width=True, hide_index=True)

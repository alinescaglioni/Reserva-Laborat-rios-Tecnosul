import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TECNOSUL - Agendamento de Labs", layout="wide")

# --- SIMULAÇÃO DE BANCO DE DADOS ---
if 'reservas' not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=[
        "ID", "Usuário", "Empresa", "Professor", "Projeto", 
        "Laboratório", "Data", "Início", "Término", "Equipamentos", "Status"
    ])

# --- CONSTANTES E REGRAS ---
LABS = ["CRIAR LAB", "MEDGEN", "CON LAB"]
EQUIPAMENTOS_MEDGEN = [
    "Banho seco com agitação", "Centrífuga refrigerada", 
    "Conjunto Micropipetas", "Espectrofotômetro Nanodrop",
    "Microcentrífuga (24 tubos)", "Sequenciador MiSeq i100",
    "Workstation DNA/RNA", "Freezer/Geladeira", "Computadores de análise"
]

def verificar_conflito(lab, data, hora_inicio, hora_fim):
    df = st.session_state.reservas
    # Filtra reservas no mesmo dia e lab que não foram reprovadas
    conflitos = df[(df['Laboratório'] == lab) & (df['Data'] == data) & (df['Status'] != "Reprovado")]
    
    if lab == "CRIAR LAB":
        return len(conflitos) >= 4  # Limite de 4 projetos
    else:
        return len(conflitos) >= 1  # Limite de 1 projeto (exclusividade)

# --- INTERFACE ---
st.title("🧪 Sistema de Agendamento de Laboratórios - TECNOSUL")

tab1, tab2 = st.tabs(["📝 Nova Solicitação", "📊 Painel de Gestão"])

with tab1:
    st.header("Formulário de Reserva")
    
    with st.form("form_reserva"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Usuário*")
            empresa = st.text_input("Empresa (se aplicável)")
            professor = st.text_input("Professor Responsável*")
            projeto = st.text_input("Nome do Projeto/Pesquisa*")
            
        with col2:
            lab_selecionado = st.selectbox("Selecione o Laboratório*", LABS)
            data_reserva = st.date_input("Data da Reserva", min_value=datetime.now())
            h_inicio = st.time_input("Hora de Início", value=time(8, 0))
            h_fim = st.time_input("Hora de Término", value=time(17, 0))

        # Regra de Horário Especial
        horario_especial = h_inicio < time(8, 0) or h_fim > time(18, 0) or data_reserva.weekday() >= 5
        
        if horario_especial:
            st.warning("⚠️ Horário fora do padrão administrativo. Upload de autorização obrigatório.")
            arquivo_auth = st.file_uploader("Upload Autorização (PDF/Imagem)", type=['pdf', 'png', 'jpg'])
        
        # Detalhamento MEDGEN
        equipamentos_sel = []
        if lab_selecionado == "MEDGEN":
            st.info("### 🧬 Protocolo MEDGEN")
            equipamentos_sel = st.multiselect("Selecione os Equipamentos:", EQUIPAMENTOS_MEDGEN)
            
            st.markdown("""
            **EPIs Obrigatórios:**
            * Jaleco, Luvas e Máscara.
            * Touca (obrigatória para cabelos soltos).
            """)
            concorda_epi = st.checkbox("Estou ciente e concordo em utilizar os EPIs obrigatórios.")

        materiais = st.text_area("Materiais de uso e consumo necessários (opcional)")
        
        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            # Validações
            erro = False
            if not nome or not professor or not projeto:
                st.error("Preencha todos os campos obrigatórios.")
                erro = True
            if horario_especial and arquivo_auth is None:
                st.error("É necessário anexar a autorização para horários especiais.")
                erro = True
            if lab_selecionado == "MEDGEN" and not concorda_epi:
                st.error("Você deve aceitar os termos de biossegurança do MEDGEN.")
                erro = True
            if verificar_conflito(lab_selecionado, data_reserva, h_inicio, h_fim):
                st.error(f"O laboratório {lab_selecionado} já atingiu a capacidade máxima para este horário.")
                erro = True

            if not erro:
                # Salvar no "Banco de Dados"
                nova_reserva = {
                    "ID": len(st.session_state.reservas) + 1,
                    "Usuário": nome, "Empresa": empresa, "Professor": professor,
                    "Projeto": projeto, "Laboratório": lab_selecionado,
                    "Data": data_reserva, "Início": h_inicio, "Término": h_fim,
                    "Equipamentos": ", ".join(equipamentos_sel),
                    "Status": "Pendente de Aprovação"
                }
                st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame([nova_reserva])], ignore_index=True)
                st.success("Solicitação enviada com sucesso! Aguarde a aprovação do Responsável (A).")

with tab2:
    st.header("Gestão e Visualização")
    
    # Filtros
    filtro_lab = st.multiselect("Filtrar por Laboratório", LABS, default=LABS)
    df_display = st.session_state.reservas[st.session_state.reservas['Laboratório'].isin(filtro_lab)]
    
    if df_display.empty:
        st.write("Nenhuma reserva encontrada.")
    else:
        # Tabela de Gestão
        st.dataframe(df_display, use_container_width=True)
        
        # Ações Administrativas (Simuladas)
        st.divider()
        st.subheader("Painel Administrativo (Aprovação)")
        id_aprov = st.number_input("ID da Reserva para Ação", step=1, min_value=1)
        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        
        if col_btn1.button("✅ Aprovar"):
            st.session_state.reservas.loc[st.session_state.reservas['ID'] == id_aprov, 'Status'] = "Aprovado"
            st.rerun()
            
        if col_btn2.button("❌ Reprovar"):
            st.session_state.reservas.loc[st.session_state.reservas['ID'] == id_aprov, 'Status'] = "Reprovado"
            st.rerun()

# --- SIDEBAR: INFO DOS LABS ---
st.sidebar.title("Informações dos Labs")
for lab in LABS:
    with st.sidebar.expander(f"Ver detalhes {lab}"):
        if lab == "MEDGEN":
            st.write("**EPIs:** Jaleco, Luvas, Máscara e Touca.")
            st.write("**Equipamentos:** Nanodrop, MiSeq i100, etc.")
        elif lab == "CRIAR LAB":
            st.write("Capacidade: Até 4 projetos simultâneos.")
        else:
            st.write("Foco: Produtos para Saúde.")

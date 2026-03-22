import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TECNOSUL - Gestão de Laboratórios", layout="wide")

# --- DICIONÁRIOS DE INVENTÁRIO (NOME: QUANTIDADE) ---
INVENTARIO = {
    "MEDGEN": {
        "Banho seco com agitação": 1,
        "Centrífuga refrigerada": 1,
        "Conjunto Micropipetas Volume Variável Autoclavável": 1,
        "Espectrofotômetro Nanodrop": 1,
        "Microcentrífuga para 24 tubos eppendorf": 1,
        "Sequenciador de DNA de última geração (MiSeq i100)": 1,
        "Workstation para DNA e RNA": 1,
        "Freezer Vertical 242L / Geladeira-Refrigerador 300L": 1,
        "Computadores para análise de dados": 1
    },
    "CRIAR LAB": {
        "Impressora 3D": 1,
        "Serrote": 1,
        "Kit de Alicates": 4,
        "Martelo": 4,
        "KIT Chave de Fenda": 3,
        "KIT Chave philips": 3,
        "Pistola de Cola Quente": 4,
        "Estação de solda": 4,
        "Estilete": 4,
        "Tesouras": 4
    },
    "CON LAB": {
        "Equipamentos de Teste de Materiais": 2,
        "Bancada de Inspeção": 2
    }
}

# --- ESTADO DO SISTEMA ---
if 'reservas' not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=[
        "ID", "Usuário", "Professor", "Projeto", "Laboratório", 
        "Data", "Início", "Término", "Equipamentos", "Status"
    ])

# --- INTERFACE ---
st.title("🧪 Sistema de Agendamento TECNOSUL")

tab1, tab2, tab3 = st.tabs(["📝 Nova Reserva", "📊 Painel de Gestão", "ℹ️ Detalhes dos Labs"])

with tab1:
    st.subheader("Solicitação de Espaço")
    
    with st.form("form_reserva"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Usuário*")
            professor = st.text_input("Professor Responsável*")
            projeto = st.text_input("Nome do Projeto/Pesquisa*")
            lab_sel = st.selectbox("Selecione o Laboratório*", list(INVENTARIO.keys()))
            
        with col2:
            data_res = st.date_input("Data*", min_value=datetime.now())
            h_ini = st.time_input("Hora Início*", value=time(8, 0))
            h_fim = st.time_input("Hora Término*", value=time(17, 0))

        st.divider()

        # --- EXIBIÇÃO DINÂMICA DE EQUIPAMENTOS E REGRAS ---
        st.write(f"### 📦 Equipamentos disponíveis em: {lab_sel}")
        
        # Formata a lista para o multiselect com as quantidades
        lista_equip_com_qtd = [f"{nome} ({qtd})" for nome, qtd in INVENTARIO[lab_sel].items()]
        equip_selecionados = st.multiselect("Selecione o que irá utilizar:", lista_equip_com_qtd)

        # Campos específicos por LAB
        if lab_sel == "CRIAR LAB":
            if any("Impressora 3D" in e for e in equip_selecionados):
                st.number_input("Quantidade de filamento (gramas):", min_value=0, step=10)
            st.info("💡 Materiais consumíveis (papelão, isopor, lápis, tintas) estão inclusos na bancada.")

        if lab_sel == "MEDGEN":
            st.warning("⚠️ **Protocolo de Biossegurança Obrigatório**")
            st.markdown("""
            - Proibido: Bermudas, saias, chinelos ou roupas de nylon.
            - Obrigatório: Jaleco, Luvas, Máscara e Touca. Cabelos longos devem estar presos.
            - **Necessário treinamento prévio nos POC's do LAB.**
            """)
            aceite = st.checkbox("Confirmo que possuo treinamento e seguirei as normas de vestimenta e EPIs.")

        # Horário Especial
        is_especial = h_ini < time(8, 0) or h_fim > time(18, 0) or data_res.weekday() >= 5
        arquivo = None
        if is_especial:
            st.error("🚨 Horário fora do padrão (08h-18h). Anexe a autorização do Coordenador.")
            arquivo = st.file_uploader("Autorização (PDF/Imagem)", type=['pdf', 'png', 'jpg'])

        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            # Lógica de validação básica (Exemplo)
            if not nome or not professor or (lab_sel == "MEDGEN" and not aceite):
                st.error("Por favor, preencha os campos obrigatórios e aceite os termos.")
            elif is_especial and arquivo is None:
                st.error("O upload da autorização é obrigatório para este horário.")
            else:
                st.success("Solicitação registrada com sucesso para análise!")

with tab2:
    st.header("Ocupação dos Laboratórios")
    st.dataframe(st.session_state.reservas, use_container_width=True)

with tab3:
    st.header("Informações Gerais e Inventário")
    
    # Criando colunas dinâmicas para os laboratórios
    cols = st.columns(len(INVENTARIO))
    
    for i, (lab, itens) in enumerate(INVENTARIO.items()):
        with cols[i]:
            st.markdown(f"#### {lab}")
            # Criando uma tabela simples para mostrar o inventário
            df_inv = pd.DataFrame(list(itens.items()), columns=["Item", "Qtd Disponível"])
            st.table(df_inv)
            
            if lab == "MEDGEN":
                st.caption("EPIs: Jaleco, Luva, Máscara, Touca.")
            elif lab == "CRIAR LAB":
                st.caption("Capacidade: 4 projetos simultâneos.")

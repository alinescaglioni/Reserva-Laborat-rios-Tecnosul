import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TECNOSUL - Gestão de Laboratórios", layout="wide")

# --- BANCO DE DADOS EM MEMÓRIA ---
if 'reservas' not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=[
        "ID", "Usuário", "Empresa", "Professor", "Projeto", 
        "Laboratório", "Data", "Início", "Término", "Equipamentos", "Status", "Filamento(g)"
    ])

# --- DICIONÁRIOS DE EQUIPAMENTOS (Com Quantidades) ---
EQUIP_MEDGEN = {
    "Banho seco com agitação (1)": 1,
    "Centrífuga refrigerada (1)": 1,
    "Conjunto Micropipetas Volume Variável (1)": 1,
    "Espectrofotômetro Nanodrop (1)": 1,
    "Microcentrífuga p/ 24 tubos (1)": 1,
    "Sequenciador MiSeq i100 (1)": 1,
    "Workstation para DNA e RNA (1)": 1,
    "Freezer/Geladeira 300L (1)": 1,
    "Computadores para análise (1)": 1
}

EQUIP_CRIAR = {
    "Impressora 3D (1)": 1,
    "Serrote (1)": 1,
    "Kit de Alicates (4)": 4,
    "Martelo (4)": 4,
    "KIT Chave de Fenda (3)": 3,
    "KIT Chave Philips (3)": 3,
    "Pistola de Cola Quente (4)": 4,
    "Estação de solda (4)": 4,
    "Estilete (4)": 4,
    "Tesouras (4)": 4
}

# --- FUNÇÕES DE VALIDAÇÃO ---
def verificar_capacidade(lab, data, h_inicio, h_fim):
    df = st.session_state.reservas
    # Filtra apenas reservas confirmadas ou pendentes no mesmo lab e dia
    conflitos = df[(df['Laboratório'] == lab) & (df['Data'] == data) & (df['Status'] != "Reprovado")]
    
    if lab == "CRIAR LAB":
        return len(conflitos) >= 4
    else:
        return len(conflitos) >= 1

# --- INTERFACE PRINCIPAL ---
st.title("🧪 Sistema de Agendamento TECNOSUL")

tab1, tab2, tab3 = st.tabs(["📝 Reserva", "📊 Gestão Administrativa", "ℹ️ Normas dos Labs"])

with tab1:
    st.header("Solicitação de Espaço e Equipamentos")
    
    with st.form("form_reserva"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Usuário*")
            empresa = st.text_input("Empresa")
            professor = st.text_input("Professor Responsável*")
            projeto = st.text_input("Nome do Projeto/Pesquisa*")
            lab_sel = st.selectbox("Laboratório*", ["CRIAR LAB", "MEDGEN", "CON LAB"])
            
        with c2:
            data_res = st.date_input("Data*", min_value=datetime.now())
            h_ini = st.time_input("Início*", value=time(8, 0))
            h_fim = st.time_input("Término*", value=time(17, 0))
            materiais_consumo = st.text_area("Materiais de uso e consumo necessários")

        # --- Lógica Específica por Lab ---
        equip_selecionados = []
        qtd_filamento = 0

        if lab_sel == "MEDGEN":
            st.warning("### 🧬 Protocolo MEDGEN - Biossegurança")
            st.markdown("""
            * **EPIs Obrigatórios:** Jaleco, Luvas, Máscara e Touca.
            * **Proibido:** Bermudas, saias, vestidos, chinelos, calçados abertos e roupas de nylon.
            * **Cabelos:** Devem estar devidamente presos.
            * **Treinamento:** É obrigatório ter treinamento nos POC's do LAB.
            """)
            equip_selecionados = st.multiselect("Equipamentos Disponíveis:", list(EQUIP_MEDGEN.keys()))
            aceite_bio = st.checkbox("Confirmo ciência das normas de Biossegurança e Treinamento POC.")

        elif lab_sel == "CRIAR LAB":
            st.info("### 🛠️ Inventário CRIAR LAB")
            equip_selecionados = st.multiselect("Ferramentas:", list(EQUIP_CRIAR.keys()))
            if "Impressora 3D (1)" in equip_selecionados:
                qtd_filamento = st.number_input("Quantidade de filamento pretendida (gramas):", min_value=0)
            st.caption("Nota: Materiais escolares (lápis, tintas, pincéis) e consumíveis básicos são disponibilizados livremente.")

        # --- Upload por Horário Especial ---
        is_especial = h_ini < time(8, 0) or h_fim > time(18, 0) or data_res.weekday() >= 5
        arquivo = None
        if is_especial:
            st.error("🚨 Horário Especial detectado: Upload de autorização do Coordenador é obrigatório.")
            arquivo = st.file_uploader("Anexar Autorização (PDF/E-mail)", type=['pdf', 'png', 'jpg'])

        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            # Validações de Negócio
            erros = []
            if not (nome and professor and projeto): erros.append("Preencha os campos obrigatórios (*).")
            if is_especial and arquivo is None: erros.append("Anexe a autorização para horários especiais.")
            if lab_sel == "MEDGEN" and not aceite_bio: erros.append("Você deve aceitar os termos do MEDGEN.")
            if verificar_capacidade(lab_sel, data_res, h_ini, h_fim): erros.append(f"Capacidade esgotada para {lab_sel} neste horário.")
            
            if erros:
                for erro in erros: st.error(erro)
            else:
                nova_res = {
                    "ID": len(st.session_state.reservas) + 1,
                    "Usuário": nome, "Empresa": empresa, "Professor": professor,
                    "Projeto": projeto, "Laboratório": lab_sel, "Data": data_res,
                    "Início": h_ini, "Término": h_fim, 
                    "Equipamentos": ", ".join(equip_selecionados),
                    "Status": "Pendente", "Filamento(g)": qtd_filamento
                }
                st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame([nova_res])], ignore_index=True)
                st.success("Solicitação enviada! O Responsável (A) analisará seu pedido.")

with tab2:
    st.header("Painel de Controle Administrativo")
    if st.session_state.reservas.empty:
        st.info("Nenhuma reserva registrada até o momento.")
    else:
        # Filtros de visualização
        f_lab = st.multiselect("Filtrar Laboratório", ["CRIAR LAB", "MEDGEN", "CON LAB"], default=["CRIAR LAB", "MEDGEN", "CON LAB"])
        df_filtrado = st.session_state.reservas[st.session_state.reservas['Laboratório'].isin(f_lab)]
        
        st.dataframe(df_filtrado, use_container_width=True)

        st.divider()
        st.subheader("Ações de Aprovação")
        id_acao = st.number_input("Digite o ID da Reserva:", min_value=1, step=1)
        c_apr, c_rep, _ = st.columns([1, 1, 4])
        
        if c_apr.button("Aprovar Reserva"):
            st.session_state.reservas.loc[st.session_state.reservas['ID'] == id_acao, 'Status'] = "Aprovada"
            st.success(f"Reserva {id_acao} aprovada. Notificação enviada ao usuário.")
            st.rerun()
            
        if c_rep.button("Reprovar Reserva"):
            st.session_state.reservas.loc[st.session_state.reservas['ID'] == id_acao, 'Status'] = "Reprovada"
            st.error(f"Reserva {id_acao} reprovada.")
            st.rerun()

with tab3:
    st.header("Informações Técnicas e Normas")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("CRIAR LAB")
        st.write("Capacidade: 4 projetos simultâneos.")
        st.write("**Ferramentas Disponíveis:**")
        for k, v in EQUIP_CRIAR.items(): st.text(f"- {k}")
        
    with col_b:
        st.subheader("MEDGEN")
        st.write("Capacidade: 1 projeto por vez (Exclusivo).")
        st.write("**Equipamentos:**")
        for k, v in EQUIP_MEDGEN.items(): st.text(f"- {k}")

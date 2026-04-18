import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="Vulcanização PRO", layout="wide")

# ----------- ESTILO -----------
st.markdown("""
<style>
.main {background-color: #f5f7fa;}
h1 {color: #0e1117;}
.stButton>button {
    background-color: #0e1117;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ----------- LOGIN -----------
def login():
    st.markdown("## 🔐 Sistema Vulcanização")
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if user == "admin" and senha == "123":
                st.session_state.logado = True
            else:
                st.error("Login inválido")

# ----------- PDF -----------
def gerar_pdf(cliente, servico, valor):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 800, "ORÇAMENTO - VULCANIZAÇÃO")

    c.setFont("Helvetica", 12)
    c.drawString(100, 760, f"Cliente: {cliente}")
    c.drawString(100, 730, f"Serviço: {servico}")
    c.drawString(100, 700, f"Valor: R$ {valor}")

    c.save()
    buffer.seek(0)
    return buffer

# ----------- APP -----------
def app():
    st.title("🛞 Vulcanização PRO")

    menu = st.sidebar.radio("Menu", ["Dashboard", "Novo Serviço"])

    if "dados" not in st.session_state:
        st.session_state.dados = []

    # -------- DASHBOARD --------
    if menu == "Dashboard":
        st.subheader("📊 Visão Geral")

        if st.session_state.dados:
            df = pd.DataFrame(st.session_state.dados)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Serviços", len(df))

            with col2:
                st.metric("Faturamento", f"R$ {df['Valor'].sum():.2f}")

            with col3:
                st.metric("Ticket Médio", f"R$ {df['Valor'].mean():.2f}")

            st.divider()

            filtro = st.text_input("🔍 Buscar cliente")

            if filtro:
                df = df[df["Cliente"].str.contains(filtro, case=False)]

            st.dataframe(df, use_container_width=True)

        else:
            st.info("Nenhum serviço cadastrado")

    # -------- NOVO SERVIÇO --------
    if menu == "Novo Serviço":
        st.subheader("➕ Novo Atendimento")

        col1, col2 = st.columns(2)

        with col1:
            cliente = st.text_input("Cliente")
            servico = st.text_input("Serviço")

        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)

        if st.button("💾 Salvar"):
            st.session_state.dados.append({
                "Cliente": cliente,
                "Serviço": servico,
                "Valor": valor
            })
            st.success("Serviço cadastrado!")

        if st.button("📄 Gerar Orçamento"):
            pdf = gerar_pdf(cliente, servico, valor)

            st.download_button(
                "Baixar PDF",
                pdf,
                file_name="orcamento.pdf",
                mime="application/pdf"
            )

# -------- EXECUÇÃO --------
if "logado" not in st.session_state:
    st.session_state.logado = False

if st.session_state.logado:
    app()
else:
    login()


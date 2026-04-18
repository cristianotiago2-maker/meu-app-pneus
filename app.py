import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
import io

# ---------------- LOGIN ----------------
def login():
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == "admin" and senha == "123":
            st.session_state.logado = True
        else:
            st.error("Login inválido")

# ---------------- PDF ----------------
def gerar_pdf(cliente, servico, valor):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    c.drawString(100, 800, "VULCANIZAÇÃO")
    c.drawString(100, 760, f"Cliente: {cliente}")
    c.drawString(100, 740, f"Serviço: {servico}")
    c.drawString(100, 720, f"Valor: R$ {valor}")

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- APP ----------------
def app():
    st.title("🛞 Sistema de Vulcanização")

    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Novo Serviço"])

    if "dados" not in st.session_state:
        st.session_state.dados = []

    if menu == "Dashboard":
        st.subheader("📊 Serviços Realizados")

        if st.session_state.dados:
            df = pd.DataFrame(st.session_state.dados)
            st.dataframe(df)

            total = df["Valor"].sum()
            st.success(f"💰 Total: R$ {total}")

        else:
            st.info("Nenhum serviço cadastrado")

    if menu == "Novo Serviço":
        st.subheader("➕ Cadastrar Serviço")

        cliente = st.text_input("Cliente")
        servico = st.text_input("Serviço")
        valor = st.number_input("Valor", min_value=0.0)

        if st.button("Salvar"):
            st.session_state.dados.append({
                "Cliente": cliente,
                "Serviço": servico,
                "Valor": valor
            })
            st.success("Salvo com sucesso!")

        if st.button("Gerar PDF"):
            pdf = gerar_pdf(cliente, servico, valor)
            st.download_button(
                label="📄 Baixar PDF",
                data=pdf,
                file_name="orcamento.pdf",
                mime="application/pdf"
            )

# ---------------- EXECUÇÃO ----------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if st.session_state.logado:
    app()
else:
    login()

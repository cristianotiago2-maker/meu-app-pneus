import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO
import plotly.express as px
from reportlab.pdfgen import canvas

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="VULCAT ERP", layout="wide")

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect("vulcat.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS clientes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
telefone TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS ordens (
id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente TEXT,
servico TEXT,
valor REAL,
data TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS estoque (
id INTEGER PRIMARY KEY AUTOINCREMENT,
produto TEXT,
qtd INTEGER
)
""")

conn.commit()

# =========================
# PDF
# =========================
def gerar_pdf(titulo, linhas):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(160, 800, titulo)

    y = 760
    pdf.setFont("Helvetica", 11)

    for linha in linhas:
        pdf.drawString(50, y, str(linha))
        y -= 18

    pdf.save()
    buffer.seek(0)
    return buffer

# =========================
# MENU
# =========================
tabs = st.tabs([
    "📊 Painel Geral",
    "🧾 Orçamentos",
    "🔧 Produção",
    "💰 Financeiro",
    "📦 Estoque",
    "👤 Clientes"
])

# =========================
# 1 PAINEL GERAL
# =========================
with tabs[0]:
    st.title("📊 Painel Geral")

    clientes = c.execute("SELECT * FROM clientes").fetchall()
    ordens = c.execute("SELECT * FROM ordens").fetchall()
    estoque = c.execute("SELECT * FROM estoque").fetchall()

    faturamento = sum([o[3] for o in ordens]) if ordens else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Clientes", len(clientes))
    col2.metric("Ordens", len(ordens))
    col3.metric("Faturamento", f"R$ {faturamento:.2f}")

    st.divider()

    # 📊 PIZZA
    st.subheader("📊 Visão Geral")
    fig = px.pie(
        names=["Clientes", "Ordens", "Estoque"],
        values=[len(clientes), len(ordens), len(estoque)]
    )
    st.plotly_chart(fig, use_container_width=True)

    # 📈 BARRA
    if ordens:
        st.subheader("📈 Faturamento por Serviço")
        df = pd.DataFrame(ordens, columns=["id","cliente","servico","valor","data"])
        fig2 = px.bar(df, x="servico", y="valor", color="servico")
        st.plotly_chart(fig2, use_container_width=True)

# =========================
# 2 ORÇAMENTOS
# =========================
with tabs[1]:
    st.title("🧾 Orçamentos")

    cliente = st.text_input("Cliente")
    servico = st.selectbox("Serviço", ["Vulcanização", "Conserto", "Troca"])
    valor = st.number_input("Valor", 0.0)

    st.subheader("👀 Pré-visualização")

    st.info(f"""
Cliente: {cliente}  
Serviço: {servico}  
Valor: R$ {valor}  
Data: {datetime.now().date()}
""")

    if st.button("Gerar Orçamento PDF"):
        data = str(datetime.now().date())

        c.execute("INSERT INTO ordens VALUES (NULL,?,?,?,?)",
                  (cliente, servico, valor, data))
        conn.commit()

        pdf = gerar_pdf("ORÇAMENTO VULCAT", [
            f"Cliente: {cliente}",
            f"Serviço: {servico}",
            f"Valor: R$ {valor}",
            f"Data: {data}"
        ])

        st.success("Orçamento gerado!")
        st.download_button("📥 Baixar PDF", pdf, "orcamento.pdf")

# =========================
# 3 PRODUÇÃO
# =========================
with tabs[2]:
    st.title("🔧 Produção (Ficha sem valores)")

    df = pd.DataFrame(
        c.execute("SELECT cliente, servico, data FROM ordens").fetchall(),
        columns=["Cliente","Serviço","Data"]
    )

    st.dataframe(df, use_container_width=True)

    if not df.empty:
        pdf = gerar_pdf("FICHA DE PRODUÇÃO", df.values.tolist())
        st.download_button("📥 PDF Produção", pdf, "producao.pdf")

# =========================
# 4 FINANCEIRO
# =========================
with tabs[3]:
    st.title("💰 Financeiro")

    ordens = c.execute("SELECT * FROM ordens").fetchall()

    total = sum([o[3] for o in ordens]) if ordens else 0

    st.metric("Faturamento Total", f"R$ {total:.2f}")

    df = pd.DataFrame(ordens, columns=["id","cliente","servico","valor","data"])
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        pdf = gerar_pdf("RELATÓRIO FINANCEIRO", df.values.tolist())
        st.download_button("📥 PDF Financeiro", pdf, "financeiro.pdf")

# =========================
# 5 ESTOQUE
# =========================
with tabs[4]:
    st.title("📦 Estoque")

    produto = st.text_input("Produto")
    qtd = st.number_input("Quantidade", 0)

    if st.button("Adicionar"):
        c.execute("INSERT INTO estoque VALUES (NULL,?,?)", (produto, qtd))
        conn.commit()

    df = pd.DataFrame(
        c.execute("SELECT * FROM estoque").fetchall(),
        columns=["ID","Produto","Qtd"]
    )

    st.dataframe(df, use_container_width=True)

    st.subheader("⚠ Alertas")

    for i in df.values:
        if i[2] < 5:
            st.warning(f"Estoque baixo: {i[1]} ({i[2]})")

# =========================
# 6 CLIENTES
# =========================
with tabs[5]:
    st.title("👤 Clientes")

    nome = st.text_input("Nome")
    tel = st.text_input("Telefone")

    if st.button("Salvar Cliente"):
        c.execute("INSERT INTO clientes VALUES (NULL,?,?)", (nome, tel))
        conn.commit()

    df = pd.DataFrame(
        c.execute("SELECT * FROM clientes").fetchall(),
        columns=["ID","Nome","Telefone"]
    )

    st.dataframe(df, use_container_width=True)

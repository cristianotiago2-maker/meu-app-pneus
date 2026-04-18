import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="VULCAT ERP ULTRA", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: white;
}
.card {
    background: #111827;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# BANCO
# =========================
conn = sqlite3.connect("vulcat_ultra.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS clientes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
telefone TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS ordens (
id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente TEXT,
servico TEXT,
valor REAL,
data TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS estoque (
id INTEGER PRIMARY KEY AUTOINCREMENT,
produto TEXT,
qtd INTEGER
)""")

conn.commit()

# =========================
# PDF
# =========================
def gerar_pdf(titulo, linhas):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(180, 800, titulo)

    y = 760
    pdf.setFont("Helvetica", 11)

    for linha in linhas:
        pdf.drawString(50, y, str(linha))
        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

# =========================
# MENU (ABAS BONITAS)
# =========================
menu = st.tabs([
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
with menu[0]:
    st.title("📊 PAINEL GERAL")  
import plotly.express as px
    clientes = c.execute("SELECT * FROM clientes").fetchall()
    ordens = c.execute("SELECT * FROM ordens").fetchall()
    estoque = c.execute("SELECT * FROM estoque").fetchall()

    faturamento = sum([o[3] for o in ordens]) if ordens else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Clientes", len(clientes))
    col2.metric("Ordens", len(ordens))
    col3.metric("Faturamento", f"R$ {faturamento:.2f}")
st.subheader("📊 Distribuição do Sistema")

labels = ["Clientes", "Ordens", "Estoque"]
values = [
    len(clientes),
    len(ordens),
    len(estoque)
]

fig = px.pie(
    names=labels,
    values=values,
    title="Visão Geral do Sistema"
)

st.plotly_chart(fig, use_container_width=True)
# =========================
# 2 ORÇAMENTOS
# =========================
with menu[1]:
    st.title("🧾 ORÇAMENTOS")

    cliente = st.text_input("Cliente")
    servico = st.selectbox("Serviço", ["Vulcanização", "Conserto", "Troca"])
    valor = st.number_input("Valor", 0.0)

    if st.button("Gerar Orçamento"):
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

        st.download_button("📥 Baixar PDF", pdf, "orcamento.pdf")

    st.dataframe(pd.read_sql("SELECT * FROM ordens", conn))

# =========================
# 3 PRODUÇÃO
# =========================
with menu[2]:
    st.title("🔧 PRODUÇÃO / FICHA")

    df = pd.read_sql("SELECT * FROM ordens", conn)

    st.dataframe(df)

    if not df.empty:
        pdf = gerar_pdf("FICHA DE PRODUÇÃO", df.values.tolist())
        st.download_button("📥 PDF Produção", pdf, "producao.pdf")

# =========================
# 4 FINANCEIRO
# =========================
with menu[3]:
    st.title("💰 FINANCEIRO")

    df = pd.read_sql("SELECT * FROM ordens", conn)

    total = df["valor"].sum() if not df.empty else 0

    st.metric("Faturamento Total", f"R$ {total:.2f}")

    if not df.empty:
        pdf = gerar_pdf("RELATÓRIO FINANCEIRO", df.values.tolist())
        st.download_button("📥 PDF Financeiro", pdf, "financeiro.pdf")

# =========================
# 5 ESTOQUE
# =========================
with menu[4]:
    st.title("📦 ESTOQUE")

    produto = st.text_input("Produto")
    qtd = st.number_input("Quantidade", 0)

    if st.button("Adicionar"):
        c.execute("INSERT INTO estoque VALUES (NULL,?,?)", (produto, qtd))
        conn.commit()

    df = pd.read_sql("SELECT * FROM estoque", conn)
    st.dataframe(df)

    if not df.empty:
        pdf = gerar_pdf("ESTOQUE", df.values.tolist())
        st.download_button("📥 PDF Estoque", pdf, "estoque.pdf")

# =========================
# 6 CLIENTES
# =========================
with menu[5]:
    st.title("👤 CLIENTES")

    nome = st.text_input("Nome")
    tel = st.text_input("Telefone")

    if st.button("Salvar Cliente"):
        c.execute("INSERT INTO clientes VALUES (NULL,?,?)", (nome, tel))
        conn.commit()

    df = pd.read_sql("SELECT * FROM clientes", conn)
    st.dataframe(df)

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# ---------------- CONFIG ----------------
st.set_page_config(page_title="VULCAT PNEUS", layout="wide", page_icon="🛞")

# ---------------- BANCO (SALVA EM CSV) ----------------
def carregar(nome):
    if os.path.exists(nome):
        return pd.read_csv(nome)
    return pd.DataFrame()

def salvar(df, nome):
    df.to_csv(nome, index=False)

clientes = carregar("clientes.csv")
estoque = carregar("estoque.csv")
financeiro = carregar("financeiro.csv")

if clientes.empty:
    clientes = pd.DataFrame(columns=["Nome", "Telefone"])
if estoque.empty:
    estoque = pd.DataFrame(columns=["Item", "Quantidade"])
if financeiro.empty:
    financeiro = pd.DataFrame(columns=["Data", "Tipo", "Valor"])

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🛞 VULCAT PNEUS")
    menu = st.radio("Menu", ["Dashboard", "Orçamento", "Estoque", "Financeiro", "Clientes"])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Painel Geral")

    entradas = financeiro[financeiro["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = financeiro[financeiro["Tipo"] == "Saída"]["Valor"].sum()
    saldo = entradas - saidas

    total_clientes = len(clientes)
    total_estoque = estoque["Quantidade"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entradas", f"R$ {entradas:,.2f}")
    c2.metric("Saídas", f"R$ {saidas:,.2f}")
    c3.metric("Saldo", f"R$ {saldo:,.2f}")
    c4.metric("Clientes", total_clientes)

    st.divider()

    col1, col2 = st.columns(2)

    if entradas > 0 or saidas > 0:
        fig = px.pie(values=[entradas, saidas], names=["Entradas", "Saídas"], hole=0.5)
        col1.plotly_chart(fig, use_container_width=True)

    if not estoque.empty:
        fig2 = px.bar(estoque, x="Item", y="Quantidade")
        col2.plotly_chart(fig2, use_container_width=True)

    # ALERTA
    baixo = estoque[estoque["Quantidade"] < 5]
    if not baixo.empty:
        st.warning("⚠️ Estoque baixo:")
        st.dataframe(baixo)

# ---------------- PDF ----------------
def gerar_pdf(cliente, itens, total):
    styles = getSampleStyleSheet()
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(file.name, pagesize=A4)

    elementos = []
    elementos.append(Paragraph("<b>VULCAT PNEUS</b>", styles['Title']))
    elementos.append(Paragraph(f"Cliente: {cliente}", styles['Normal']))
    elementos.append(Spacer(1, 12))

    data = [["Item", "Qtd", "Valor", "Total"]]
    for _, row in itens.iterrows():
        total_item = row["Qtd"] * row["Valor"]
        data.append([row["Item"], row["Qtd"], row["Valor"], total_item])

    tabela = Table(data)
    tabela.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))
    elementos.append(tabela)

    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"Total: R$ {total:.2f}", styles['Heading2']))

    doc.build(elementos)
    return file.name

# ---------------- ORÇAMENTO ----------------
elif menu == "Orçamento":
    st.title("📄 Orçamento")

    cliente = st.selectbox("Cliente", [""] + clientes["Nome"].tolist())

    df = pd.DataFrame([{"Item": "", "Qtd": 1, "Valor": 0.0}])
    edit = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    total = (edit["Qtd"] * edit["Valor"]).sum()
    st.metric("Total", f"R$ {total:,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salvar como Entrada"):
            financeiro.loc[len(financeiro)] = [datetime.now(), "Entrada", total]
            salvar(financeiro, "financeiro.csv")
            st.success("Salvo!")

    with col2:
        if st.button("📄 Gerar PDF"):
            if cliente == "":
                st.warning("Selecione um cliente")
            else:
                pdf = gerar_pdf(cliente, edit, total)
                with open(pdf, "rb") as f:
                    st.download_button("⬇️ Baixar PDF", f, "orcamento.pdf")

# ---------------- ESTOQUE ----------------
elif menu == "Estoque":
    st.title("📦 Estoque")

    estoque = st.data_editor(estoque, num_rows="dynamic", use_container_width=True)

    if st.button("Salvar Estoque"):
        salvar(estoque, "estoque.csv")
        st.success("Salvo!")

# ---------------- FINANCEIRO ----------------
elif menu == "Financeiro":
    st.title("💰 Financeiro")

    financeiro = st.data_editor(financeiro, num_rows="dynamic", use_container_width=True)

    if st.button("Salvar Financeiro"):
        salvar(financeiro, "financeiro.csv")
        st.success("Salvo!")

# ---------------- CLIENTES ----------------
elif menu == "Clientes":
    st.title("👥 Clientes")

    clientes = st.data_editor(clientes, num_rows="dynamic", use_container_width=True)

    if st.button("Salvar Clientes"):
        salvar(clientes, "clientes.csv")
        st.success("Salvo!")

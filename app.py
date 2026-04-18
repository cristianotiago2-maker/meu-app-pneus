import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

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
quantidade INTEGER
)
""")

conn.commit()

# =========================
# MENU
# =========================
st.sidebar.title("⚙ VULCAT ERP")
menu = st.sidebar.radio("Menu", ["Dashboard", "Clientes", "Ordem", "Estoque"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    clientes = c.execute("SELECT * FROM clientes").fetchall()
    ordens = c.execute("SELECT * FROM ordens").fetchall()

    faturamento = sum([o[3] for o in ordens]) if ordens else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Clientes", len(clientes))
    col2.metric("Ordens", len(ordens))
    col3.metric("Faturamento", f"R$ {faturamento:.2f}")

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.title("👤 Clientes")

    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")

    if st.button("Salvar Cliente"):
        c.execute("INSERT INTO clientes VALUES (NULL,?,?)", (nome, telefone))
        conn.commit()
        st.success("Cliente salvo!")

    df = pd.read_sql("SELECT * FROM clientes", conn)
    st.dataframe(df)

# =========================
# ORDEM DE SERVIÇO
# =========================
elif menu == "Ordem":
    st.title("🧾 Ordem de Serviço")

    cliente = st.text_input("Cliente")
    servico = st.selectbox("Serviço", ["Vulcanização", "Conserto", "Troca"])
    valor = st.number_input("Valor", 0.0)

    if st.button("Criar Ordem"):
        data = str(datetime.now().date())

        c.execute("INSERT INTO ordens VALUES (NULL,?,?,?,?)",
                  (cliente, servico, valor, data))
        conn.commit()

        st.success("Ordem criada!")

    df = pd.read_sql("SELECT * FROM ordens", conn)
    st.dataframe(df)

# =========================
# ESTOQUE
# =========================
elif menu == "Estoque":
    st.title("📦 Estoque")

    produto = st.text_input("Produto")
    qtd = st.number_input("Quantidade", 0)

    if st.button("Adicionar"):
        c.execute("INSERT INTO estoque VALUES (NULL,?,?)", (produto, qtd))
        conn.commit()
        st.success("Item adicionado!")

    df = pd.read_sql("SELECT * FROM estoque", conn)
    st.dataframe(df)

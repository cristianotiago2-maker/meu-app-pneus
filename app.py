import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas

# =========================
# BANCO
# =========================
conn = sqlite3.connect("vulcat_saas.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS empresas (
id INTEGER PRIMARY KEY,
nome TEXT,
plano TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
id INTEGER PRIMARY KEY,
empresa_id INTEGER,
user TEXT,
password TEXT,
role TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS ordens (
id INTEGER PRIMARY KEY,
empresa_id INTEGER,
cliente TEXT,
servico TEXT,
valor REAL,
data TEXT
)""")

conn.commit()

# =========================
# UTIL
# =========================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# empresa demo (SaaS base)
def criar_empresa_demo():
    c.execute("SELECT * FROM empresas")
    if not c.fetchall():
        c.execute("INSERT INTO empresas VALUES (NULL,?,?)",
                  ("VULCAT DEMO", "PRO"))
        empresa_id = c.lastrowid

        c.execute("INSERT INTO usuarios VALUES (NULL,?,?,?,?)",
                  (empresa_id, "admin", hash_pw("1234"), "admin"))
        conn.commit()

criar_empresa_demo()

# =========================
# LOGIN SAAS
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.empresa_id = None

if not st.session_state.logado:
    st.title("🚀 VULCAT SAAS LOGIN")

    user = st.text_input("Usuário")
    pw = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        c.execute("""
        SELECT empresa_id, role FROM usuarios 
        WHERE user=? AND password=?
        """, (user, hash_pw(pw)))

        result = c.fetchone()

        if result:
            st.session_state.logado = True
            st.session_state.empresa_id = result[0]
            st.success("Login OK")
        else:
            st.error("Erro login")

    st.stop()

empresa_id = st.session_state.empresa_id

# =========================
# MENU
# =========================
st.sidebar.title("⚙ SAAS MENU")

menu = st.sidebar.radio("Navegação", [
    "Dashboard",
    "Clientes",
    "Orçamentos"
])

# =========================
# DASHBOARD SAAS
# =========================
if menu == "Dashboard":
    st.title("📊 DASHBOARD SAAS")

    ordens = pd.read_sql(f"""
    SELECT * FROM ordens WHERE empresa_id={empresa_id}
    """, conn)

    col1, col2 = st.columns(2)

    col1.metric("Ordens", len(ordens))
    col2.metric("Faturamento", f"R$ {ordens['valor'].sum() if not ordens.empty else 0}")

# =========================
# CLIENTES (SIMPLES SAAS)
# =========================
elif menu == "Clientes":
    st.title("👤 CLIENTES")

    nome = st.text_input("Nome")
    tel = st.text_input("Telefone")

    if st.button("Salvar"):
        st.success("Aqui você pode expandir com tabela clientes por empresa")

# =========================
# ORÇAMENTOS SAAS
# =========================
elif menu == "Orçamentos":
    st.title("🧾 ORÇAMENTOS SAAS")

    cliente = st.text_input("Cliente")
    servico = st.selectbox("Serviço", ["Vulcanização", "Conserto", "Troca"])
    valor = st.number_input("Valor", 0.0)

    if st.button("Criar"):
        data = str(datetime.now().date())

        c.execute("""
        INSERT INTO ordens VALUES (NULL,?,?,?,?,?)
        """, (empresa_id, cliente, servico, valor, data))

        conn.commit()

        st.success("Orçamento criado!")

    ordens = pd.read_sql(f"""
    SELECT * FROM ordens WHERE empresa_id={empresa_id}
    """, conn)

    st.dataframe(ordens)

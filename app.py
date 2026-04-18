import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -------- CONFIG --------
st.set_page_config(page_title="VULCAT PNEUS", layout="wide")

# -------- ESTILO --------
st.markdown("""
<style>
.main {background-color: #0E1117;}
h1, h2, h3 {color: white;}
[data-testid="metric-container"] {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------- LOGIN --------
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login - VULCAT PNEUS")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == "admin" and senha == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Login inválido")

    st.stop()

# -------- FUNÇÕES --------
def carregar(nome, colunas):
    if os.path.exists(nome):
        return pd.read_csv(nome)
    return pd.DataFrame(columns=colunas)

def salvar(df, nome):
    df.to_csv(nome, index=False)

# -------- BANCO --------
clientes = carregar("clientes.csv", ["Nome", "Telefone"])
estoque = carregar("estoque.csv", ["Item", "Quantidade"])
financeiro = carregar("financeiro.csv", ["Data", "Tipo", "Valor"])

# -------- SIDEBAR --------
with st.sidebar:
    st.title("🛞 VULCAT")
    menu = st.radio("Menu", ["Dashboard", "Orçamento", "Estoque", "Financeiro", "Clientes"])
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

# -------- DASHBOARD --------
if menu == "Dashboard":
    st.title("📊 Painel Geral")

    entradas = financeiro[financeiro["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = financeiro[financeiro["Tipo"] == "Saída"]["Valor"].sum()
    saldo = entradas - saidas

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entradas", f"R$ {entradas:,.2f}")
    c2.metric("Saídas", f"R$ {saidas:,.2f}")
    c3.metric("Saldo", f"R$ {saldo:,.2f}")
    c4.metric("Clientes", len(clientes))

    st.divider()

    if not estoque.empty:
        st.subheader("📦 Estoque")
        st.dataframe(estoque)

    baixo = estoque[estoque["Quantidade"] < 5]
    if not baixo.empty:
        st.warning("⚠️ Estoque baixo")
        st.dataframe(baixo)

# -------- ORÇAMENTO --------
elif menu == "Orçamento":
    st.title("📄 Orçamento")

    cliente = st.selectbox("Cliente", [""] + clientes["Nome"].tolist())

    item = st.text_input("Serviço/Produto")
    qtd = st.number_input("Qtd", min_value=1, value=1)
    valor = st.number_input("Valor", min_value=0.0)

    total = qtd * valor
    st.metric("Total", f"R$ {total:,.2f}")

    if st.button("Salvar como entrada"):
        if cliente == "":
            st.warning("Selecione um cliente")
        else:
            novo = pd.DataFrame([[datetime.now(), "Entrada", total]],
                                columns=["Data", "Tipo", "Valor"])
            financeiro = pd.concat([financeiro, novo], ignore_index=True)
            salvar(financeiro, "financeiro.csv")
            st.success("Salvo no financeiro!")

# -------- ESTOQUE --------
elif menu == "Estoque":
    st.title("📦 Estoque")

    item = st.text_input("Item")
    qtd = st.number_input("Quantidade", min_value=0)

    if st.button("Adicionar"):
        novo = pd.DataFrame([[item, qtd]], columns=["Item", "Quantidade"])
        estoque = pd.concat([estoque, novo], ignore_index=True)
        salvar(estoque, "estoque.csv")
        st.success("Adicionado!")

    st.dataframe(estoque)

# -------- FINANCEIRO --------
elif menu == "Financeiro":
    st.title("💰 Financeiro")

    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
    valor = st.number_input("Valor", min_value=0.0)

    if st.button("Salvar"):
        novo = pd.DataFrame([[datetime.now(), tipo, valor]],
                            columns=["Data", "Tipo", "Valor"])
        financeiro = pd.concat([financeiro, novo], ignore_index=True)
        salvar(financeiro, "financeiro.csv")
        st.success("Salvo!")

    st.dataframe(financeiro)

# -------- CLIENTES --------
elif menu == "Clientes":
    st.title("👥 Clientes")

    nome = st.text_input("Nome")
    tel = st.text_input("Telefone")

    if st.button("Adicionar"):
        novo = pd.DataFrame([[nome, tel]], columns=["Nome", "Telefone"])
        clientes = pd.concat([clientes, novo], ignore_index=True)
        salvar(clientes, "clientes.csv")
        st.success("Cliente salvo!")

    st.dataframe(clientes)

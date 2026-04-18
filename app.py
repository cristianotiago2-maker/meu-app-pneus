
(sem assunto)
Caixa de entrada

Tiago Cristiano da Silva <cristianotiago2@gmail.com>
08:22 (há 2 minutos)
para mim

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA E BANCO DE DADOS
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

def init_db():
    conn = sqlite3.connect('agrofrota.db')
    c = conn.cursor()
    # Tabela de Pneus
    c.execute('''CREATE TABLE IF NOT EXISTS pneus 
                 (id INTEGER PRIMARY KEY, tipo TEXT, marca TEXT, medida TEXT, qtd INTEGER)''')
    # Tabela de Clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes 
                 (id INTEGER PRIMARY KEY, nome TEXT, documento TEXT, cidade TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# 2. ESTILO VISUAL (MANTENDO O QUE VOCÊ GOSTOU)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffa2; }
    .card { background-color: #1e2130; padding: 20px; border-radius: 15px; border-left: 5px solid #00ffa2; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. MENU LATERAL
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)
    menu = st.selectbox("Navegação", ["📊 Dashboard", "🛞 Estoque Pneus", "👥 Clientes", "🛠️ Produção"])

# 4. MÓDULO: DASHBOARD
if menu == "📊 Dashboard":
    st.title("🚀 Painel de Controle")
    col1, col2, col3, col4 = st.columns(4)
    
    # Busca dados reais do banco para o dashboard
    total_pneus = pd.read_sql("SELECT SUM(qtd) as total FROM pneus", conn)['total'][0] or 0
    total_clientes = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'][0]
    
    col1.metric("Saldo Atual", "R$ 450,00")
    col2.metric("Entradas", "R$ 500,00")
    col3.metric("Itens Estoque", int(total_pneus))
    col4.metric("Clientes Ativos", int(total_clientes))

# 5. MÓDULO: ESTOQUE (COM SALVAMENTO REAL)
elif menu == "🛞 Estoque Pneus":
    st.title("🛞 Gestão de Estoque")
    
    with st.form("form_pneus"):
        c1, c2, c3 = st.columns(3)
        t = c1.selectbox("Tipo", ["Agrícola", "Rodoviário"])
        m = c2.text_input("Marca")
        med = c3.text_input("Medida")
        q = st.number_input("Quantidade", min_value=0)
        if st.form_submit_button("Salvar no Banco de Dados"):
            conn.execute("INSERT INTO pneus (tipo, marca, medida, qtd) VALUES (?,?,?,?)", (t, m, med, q))
            conn.commit()
            st.success("Salvo com sucesso!")

    st.subheader("Itens Cadastrados")
    df_pneus = pd.read_sql("SELECT tipo, marca, medida, qtd FROM pneus", conn)
    st.dataframe(df_pneus, use_container_width=True)

# 6. MÓDULO: CLIENTES (COM SALVAMENTO REAL)
elif menu == "👥 Clientes":
    st.title("👥 Cadastro de Clientes")
    
    with st.expander("➕ Adicionar Novo Cliente"):
        nome = st.text_input("Nome/Razão Social")
        doc = st.text_input("CPF/CNPJ")
        cid = st.text_input("Cidade")
        if st.button("Cadastrar"):
            conn.execute("INSERT INTO clientes (nome, documento, cidade) VALUES (?,?,?)", (nome, doc, cid))
            conn.commit()
            st.rerun()

    st.subheader("Lista de Clientes")
    df_cli = pd.read_sql("SELECT nome, documento, cidade FROM clientes", conn)
    for index, row in df_cli.iterrows():
        st.markdown(f"""<div class="card"><b>{row['nome']}</b><br>{row['documento']} | {row['cidade']}</div>""", unsafe_allow_html=True)

# 7. MÓDULO: PRODUÇÃO
elif menu == "🛠️ Produção":
    st.title("🛠️ Ficha de Produção")
    st.info("Aqui você pode vincular os pneus cadastrados aos clientes para serviços.")
    # Lista clientes do banco para o selectbox
    clientes_list = pd.read_sql("SELECT nome FROM clientes", conn)['nome'].tolist()
    if clientes_list:
        sel_cliente = st.selectbox("Selecione o Cliente", clientes_list)
        servico = st.multiselect("Serviço", ["Recapagem", "Montagem", "Vulcanização"])
        if st.button("Gerar Ordem de Serviço"):
            st.success(f"OS gerada para {sel_cliente}!")
    else:
        st.warning("Cadastre um cliente primeiro!")


import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# 1. CONFIGURAÇÃO E ESTILO "DARK AGRO"
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 35px; color: #00ffa2; font-weight: bold; }
    .stSelectbox label, .stTextInput label { color: #00ffa2 !important; }
    [data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 4px solid #00ffa2;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS
def get_connection():
    return sqlite3.connect('agrofrota_vfinal.db', check_same_thread=False)

# 3. MENU LATERAL
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)
    st.write("---")
    menu = st.selectbox("Navegação", ["📊 Dashboard", "🛞 Estoque Pneus", "👥 Clientes", "🛠️ Produção"])

# 4. MODELO: DASHBOARD (ITENS EM CIMA + PIZZA EMBAIXO)
if menu == "📊 Dashboard":
    st.markdown("### 📈 Visão Geral do Sistema")
    
    conn = get_connection()
    df_pneus = pd.read_sql("SELECT tipo, qtd FROM pneus", conn)
    total_cli = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'].iloc[0]
    conn.close()

    # --- LINHA SUPERIOR: ITENS ---
    col1, col2, col3, col4 = st.columns(4)
    total_est = df_pneus['qtd'].sum() if not df_pneus.empty else 0
    
    col1.metric("Estoque Total", f"{total_est} un")
    col2.metric("Clientes Ativos", total_cli)
    col3.metric("Produção", "92%", "Ok")
    col4.metric("Financeiro", "R$ 850k", "+12%")

    st.write("---")

    # --- LINHA INFERIOR: GRÁFICO DE PIZZA ---
    st.markdown("<h3 style='text-align: center;'>🎯 Distribuição por Segmento</h3>", unsafe_allow_html=True)
    
    if not df_pneus.empty:
        # Criando o gráfico de pizza (Donut Chart)
        fig = px.pie(
            df_pneus, 
            values='qtd', 
            names='tipo', 
            hole=0.5,
            color_discrete_sequence=['#00ffa2', '#0288d1'] # Verde e Azul Agro
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            showlegend=True,
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cadastre pneus para gerar o gráfico.")

# 5. MÓDULO ESTOQUE (CADASTRO)
elif menu == "🛞 Estoque Pneus":
    st.header("🛞 Gestão de Estoque")
    with st.form("cadastro"):
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo", ["Agrícola", "Rodoviário"])
        marca = c2.text_input("Marca")
        medida = st.text_input("Medida")
        qtd = st.number_input("Quantidade", min_value=1, step=1)
        if st.form_submit_button("Salvar Registro"):
            conn = get_connection()
            conn.execute("INSERT INTO pneus (tipo, marca, medida, qtd) VALUES (?,?,?,?)", (tipo, marca, medida, qtd))
            conn.commit()
            st.success("Salvo!")
            st.rerun()

# 6. MÓDULO CLIENTES
elif menu == "👥 Clientes":
    st.header("👥 Clientes")
    with st.form("cli"):
        n = st.text_input("Nome")
        d = st.text_input("CPF/CNPJ")
        if st.form_submit_button("Adicionar"):
            conn = get_connection()
            conn.execute("INSERT INTO clientes (nome, documento) VALUES (?,?)", (n, d))
            conn.commit()
            st.rerun()

# 7. MÓDULO PRODUÇÃO
elif menu == "🛠️ Produção":
    st.header("🛠️ Ordem de Produção")
    st.info("Selecione os dados para gerar a ficha em PDF.")










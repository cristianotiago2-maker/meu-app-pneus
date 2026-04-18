import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

# --- ESTILO VISUAL (Navegação Superior e Cards) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130;
        border-radius: 10px 10px 0px 0px;
        color: white;
        padding: 10px 25px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { border-bottom: 4px solid #00ffa2 !important; color: #00ffa2 !important; }
    [data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 4px solid #00ffa2;
    }
    div[data-testid="stMetricValue"] { color: #00ffa2; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def get_connection():
    conn = sqlite3.connect('agrofrota_vfinal.db', check_same_thread=False)
    # Criar tabela financeiro se não existir
    conn.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, tipo TEXT, data TEXT)')
    return conn

# --- CABEÇALHO ---
st.markdown("<h1 style='text-align: center; color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO SUPERIOR ---
tab_dash, tab_fin, tab_est, tab_cli, tab_prod = st.tabs([
    "📊 DASHBOARD", "💰 FINANCEIRO", "🛞 ESTOQUE", "👥 CLIENTES", "🛠️ PRODUÇÃO"
])

# --- 1. MÓDULO DASHBOARD ---
with tab_dash:
    conn = get_connection()
    df_pneus = pd.read_sql("SELECT tipo, qtd FROM pneus", conn)
    df_fin = pd.read_sql("SELECT valor, tipo FROM financeiro", conn)
    conn.close()

    # Cálculo Financeiro para o Topo
    receita = df_fin[df_fin['tipo'] == 'Receita']['valor'].sum()
    despesa = df_fin[df_fin['tipo'] == 'Despesa']['valor'].sum()
    saldo = receita - despesa

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo em Caixa", f"R$ {saldo:,.2f}")
    c2.metric("Pneus em Estoque", int(df_pneus['qtd'].sum()) if not df_pneus.empty else 0)
    c3.metric("Total Receitas", f"R$ {receita:,.2f}")
    c4.metric("Total Despesas", f"R$ {despesa:,.2f}")

    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>🎯 Distribuição de Pneus</h3>", unsafe_allow_html=True)
    if not df_pneus.empty:
        fig = px.pie(df_pneus, values='qtd', names='tipo', hole=0.5, color_discrete_sequence=['#00ffa2', '#0288d1'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- 2. MÓDULO FINANCEIRO ---
with tab_fin:
    st.subheader("💰 Gestão de Caixa")
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.markdown("### Novo Lançamento")
        with st.form("form_fin"):
            desc = st.text_input("Descrição")
            val = st.number_input("Valor (R$)", min_value=0.01)
            tipo_f = st.selectbox("Tipo", ["Receita", "Despesa"])
            if st.form_submit_button("Confirmar Lançamento"):
                conn = get_connection()
                conn.execute("INSERT INTO financeiro (descricao, valor, tipo, data) VALUES (?,?,?,?)", 
                             (desc, val, tipo_f, pd.Timestamp.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success("Lançado!")
                st.rerun()

    with col_f2:
        st.markdown("### Histórico Recente")
        conn = get_connection()
        df_historico = pd.read_sql("SELECT data, descricao, tipo, valor FROM financeiro ORDER BY id DESC LIMIT 10", conn)
        conn.close()
        st.dataframe(df_historico, use_container_width=True)

# --- 3. MÓDULO ESTOQUE ---
with tab_est:
    st.subheader("🛞 Controle de Estoque")
    # ... (mesmo código de cadastro de pneus que usamos antes)
    with st.form("pneus_est"):
        c_a, c_b = st.columns(2)
        tipo_p = c_a.selectbox("Segmento", ["Agrícola", "Rodoviário"])
        marca_p = c_b.text_input("Marca")
        med_p = st.text_input("Medida")
        qtd_p = st.number_input("Quantidade", min_value=1)
        if st.form_submit_button("Salvar"):
            conn = get_connection()
            conn.execute("INSERT INTO pneus (tipo, marca, medida, qtd) VALUES (?,?,?,?)", (tipo_p, marca_p, med_p, qtd_p))
            conn.commit()
            st.rerun()

# --- 4. MÓDULO CLIENTES ---
with tab_cli:
    st.subheader("👥 Clientes")
    # ... (mesmo código de clientes)

# --- 5. MÓDULO PRODUÇÃO ---
with tab_prod:
    st.subheader("🛠️ Produção")
    # ... (mesmo código de PDF)











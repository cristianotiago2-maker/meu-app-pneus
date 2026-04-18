import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { background-color: #1e2130; border-radius: 10px 10px 0px 0px; color: white; padding: 10px 25px; font-weight: bold; }
    .stTabs [aria-selected="true"] { border-bottom: 4px solid #00ffa2 !important; color: #00ffa2 !important; }
    [data-testid="stMetric"] { background-color: #1e2130; padding: 20px; border-radius: 15px; border-bottom: 4px solid #00ffa2; }
    div[data-testid="stMetricValue"] { color: #00ffa2; }
    .card-sistema { background-color: #1e2130; padding: 20px; border-radius: 15px; border-left: 5px solid #00ffa2; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def get_connection():
    conn = sqlite3.connect('agrofrota_vfinal.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS pneus (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, marca TEXT, medida TEXT, qtd INTEGER, preco REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, documento TEXT, endereco TEXT, telefone TEXT, email TEXT, obs TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, tipo TEXT, data TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS producao (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, pneu TEXT, servico TEXT, entrada TEXT, saida TEXT, status TEXT)')
    return conn

def gerar_pdf_os(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AGRO-FROTA - ORDEM DE SERVIÇO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    for k, v in dados.items():
        pdf.cell(0, 10, f"{k}: {v}", ln=True)
    return pdf.output()

# --- INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)

tab_dash, tab_fin, tab_est, tab_cli, tab_prod = st.tabs([
    "📊 DASHBOARD", "💰 FINANCEIRO", "🛞 ESTOQUE", "👥 CLIENTES", "🛠️ PRODUÇÃO"
])

# DASHBOARD
with tab_dash:
    conn = get_connection()
    df_pneus = pd.read_sql("SELECT tipo, qtd FROM pneus", conn)
    df_fin = pd.read_sql("SELECT valor, tipo FROM financeiro", conn)
    total_cli_q = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)
    total_cli = int(total_cli_q['total'].iloc[0])
    conn.close()

    rec = df_fin[df_fin['tipo'] == 'Receita']['valor'].sum()
    des = df_fin[df_fin['tipo'] == 'Despesa']['valor'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo Caixa", f"R$ {rec - des:,.2f}")
    c2.metric("Itens Estoque", int(df_pneus['qtd'].sum()) if not df_pneus.empty else 0)
    c3.metric("Clientes Ativos", total_cli)
    c4.metric("Produtividade", "92%")

    st.markdown("---")
    if not df_pneus.empty:
        fig = px.pie(df_pneus, values='qtd', names='tipo', hole=0.5, color_discrete_sequence=['#00ffa2', '#0288d1'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

# FINANCEIRO
with tab_fin:
    st.subheader("💰 Gestão Financeira")
    with st.form("fin_form"):
        col_f1, col_f2, col_f3 = st.columns(3)
        d_fin = col_f1.text_input("Descrição")
        v_fin = col_f2.number_input("Valor", min_value=0.0)
        t_fin = col_f3.selectbox("Tipo", ["Receita", "Despesa"])
        if st.form_submit_button("Lançar"):
            conn = get_connection()
            conn.execute("INSERT INTO financeiro (descricao, valor, tipo, data) VALUES (?,?,?,?)", 
                         (d_fin, v_fin, t_fin, datetime.now().strftime('%d/%m/%Y')))
            conn.commit()
            st.rerun()

# PRODUÇÃO
with tab_prod:
    st.subheader("🛠️ Ordens de Serviço")
    with st.expander("📥 Abrir O.S. (Entrada)"):
        with st.form("os_form"):
            c_o1, c_o2 = st.columns(2)
            cli_os = c_o1.text_input("Cliente")
            pneu_os = c_o2.text_input("Pneu")
            serv_os = st.selectbox("Serviço", ["Recapagem", "Montagem", "Vulcanização"])
            if st.form_submit_button("Registrar Entrada"):
                conn = get_connection()
                ent = datetime.now().strftime('%d/%m/%Y %H:%M')
                conn.execute("INSERT INTO producao (cliente, pneu, servico, entrada, status) VALUES (?,?,?,?,?)", (cli_os, pneu_os, serv_os, ent, "Aberto"))
                conn.commit()
                st.rerun()















import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

# --- ESTILO VISUAL MANTIDO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1e2130; border-radius: 10px 10px 0px 0px; 
        color: white; padding: 10px 25px; font-weight: bold; 
    }
    .stTabs [aria-selected="true"] { border-bottom: 4px solid #00ffa2 !important; color: #00ffa2 !important; }
    [data-testid="stMetric"] { 
        background-color: #1e2130; padding: 20px; border-radius: 15px; border-bottom: 4px solid #00ffa2; 
    }
    div[data-testid="stMetricValue"] { color: #00ffa2; font-size: 32px; }
    .card-sistema { 
        background-color: #1e2130; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #00ffa2; margin-bottom: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS (COM PROTEÇÃO CONTRA ERROS) ---
def get_connection():
    conn = sqlite3.connect('agrofrota_v_estavel.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS pneus (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, marca TEXT, medida TEXT, qtd INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, documento TEXT, endereco TEXT, telefone TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, tipo TEXT, data TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS producao (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, pneu TEXT, entrada TEXT)')
    conn.commit()
    return conn

conn = get_connection()

# --- BARRA LATERAL ---
with st.sidebar:
    st.subheader("⚙️ Configurações")
    nome_sistema = st.text_input("Nome da Empresa", value="AGRO-FROTA")
    st.write("---")

st.markdown(f"<h1 style='text-align: center; color: #00ffa2;'>🚜 {nome_sistema.upper()}</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO SUPERIOR ---
tab_dash, tab_fin, tab_est, tab_cli, tab_prod = st.tabs([
    "📊 DASHBOARD", "💰 FINANCEIRO", "🛞 ESTOQUE", "👥 CLIENTES", "🛠️ PRODUÇÃO"
])

# 1. DASHBOARD
with tab_dash:
    df_p = pd.read_sql("SELECT tipo, qtd FROM pneus", conn)
    df_f = pd.read_sql("SELECT valor, tipo FROM financeiro", conn)
    total_cli = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'].iloc[0]
    
    receitas = df_f[df_f['tipo'] == 'Receita']['valor'].sum()
    despesas = df_f[df_f['tipo'] == 'Despesa']['valor'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo Caixa", f"R$ {receitas - despesas:,.2f}")
    c2.metric("Qtd Estoque", int(df_p['qtd'].sum()) if not df_p.empty else 0)
    c3.metric("Clientes", total_cli)
    c4.metric("Status", "Ativo")

    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>🎯 Distribuição de Estoque</h3>", unsafe_allow_html=True)
    if not df_p.empty:
        fig = px.pie(df_p, values='qtd', names='tipo', hole=0.5, color_discrete_sequence=['#00ffa2', '#0288d1'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cadastre pneus para ativar o gráfico.")

# 2. FINANCEIRO
with tab_fin:
    st.subheader("💰 Novo Lançamento")
    with st.form("f_fin", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        desc_f = col_f1.text_input("Descrição")
        val_f = col_f2.number_input("Valor", min_value=0.0)
        tipo_f = col_f3.selectbox("Tipo", ["Receita", "Despesa"])
        if st.form_submit_button("Registrar"):
            conn.execute("INSERT INTO financeiro (descricao, valor, tipo, data) VALUES (?,?,?,?)", 
                         (desc_f, val_f, tipo_f, datetime.now().strftime('%d/%m/%Y')))
            conn.commit()
            st.rerun()

# 3. ESTOQUE (BOTÃO APAGAR)
with tab_est:
    st.subheader("🛞 Gestão de Pneus")
    with st.expander("➕ Novo Pneu"):
        with st.form("f_est", clear_on_submit=True):
            e1, e2 = st.columns(2)
            t_e = e1.selectbox("Tipo", ["Agrícola", "Rodoviário"])
            m_e = e2.text_input("Marca/Modelo")
            q_e = st.number_input("Qtd", min_value=1)
            if st.form_submit_button("Salvar"):
                conn.execute("INSERT INTO pneus (tipo, marca, qtd) VALUES (?,?,?)", (t_e, m_e, q_e))
                conn.commit()
                st.rerun()
    
    df_estoque = pd.read_sql("SELECT * FROM pneus", conn)
    for i, r in df_estoque.iterrows():
        col_list = st.columns([4, 1])
        col_list[0].write(f"**{r['tipo']}** - {r['marca']} ({r['qtd']} un)")
        if col_list[1].button("🗑️", key=f"del_p_{r['id']}"):
            conn.execute(f"DELETE FROM pneus WHERE id={r['id']}")
            conn.commit()
            st.rerun()

# 4. CLIENTES (BOTÃO EDITAR E APAGAR)
with tab_cli:
    st.subheader("👥 Cadastro de Clientes")
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    
    with st.expander("📝 Formulário", expanded=True if st.session_state.edit_id else False):
        curr = [""] * 4
        if st.session_state.edit_id:
            curr = conn.execute("SELECT nome, documento, endereco, telefone FROM clientes WHERE id=?", (st.session_state.edit_id,)).fetchone()
        
        with st.form("f_cli", clear_on_submit=True):
            nome_c = st.text_input("Nome", value=curr[0])
            doc_c = st.text_input("CNPJ/CPF", value=curr[1])
            end_c = st.text_input("Endereço", value=curr[2])
            tel_c = st.text_input("Telefone", value=curr[3])
            if st.form_submit_button("💾 Salvar"):
                if st.session_state.edit_id:
                    conn.execute("UPDATE clientes SET nome=?, documento=?, endereco=?, telefone=? WHERE id=?", (nome_c, doc_c, end_c, tel_c, st.session_state.edit_id))
                    st.session_state.edit_id = None
                else:
                    conn.execute("INSERT INTO clientes (nome, documento, endereco, telefone) VALUES (?,?,?,?)", (nome_c, doc_c, end_c, tel_c))
                conn.commit()
                st.rerun()

    df_cli = pd.read_sql("SELECT * FROM clientes", conn)
    for i, r in df_cli.iterrows():
        with st.container():
            st.markdown(f'<div class="card-sistema"><b>{r["nome"]}</b> - {r["documento"]}</div>', unsafe_allow_html=True)
            b1, b2, _ = st.columns([1, 1, 4])
            if b1.button("📝", key=f"ed_c_{r['id']}"): 
                st.session_state.edit_id = r['id']
                st.rerun()
            if b2.button("🗑️", key=f"de_c_{r['id']}"):
                conn.execute(f"DELETE FROM clientes WHERE id={r['id']}")
                conn.commit()
                st.rerun()

# 5. PRODUÇÃO
with tab_prod:
    st.subheader("🛠️ Ordens de Serviço")
    with st.form("f_os", clear_on_submit=True):
        o1, o2 = st.columns(2)
        c_o = o1.text_input("Cliente")
        p_o = o2.text_input("Pneu")
        if st.form_submit_button("Abrir O.S."):
            ent = datetime.now().strftime('%d/%m/%Y %H:%M')
            conn.execute("INSERT INTO producao (cliente, pneu, entrada) VALUES (?,?,?)", (c_o, p_o, ent))
            conn.commit()
            st.rerun()
















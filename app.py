import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO E ESTILO (VISUAL OFICIAL MANTIDO) ---
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* Estilo das Abas Superiores */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130; border-radius: 10px 10px 0px 0px;
        color: white; padding: 10px 25px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { border-bottom: 4px solid #00ffa2 !important; color: #00ffa2 !important; }
    
    /* Cards do Dashboard */
    [data-testid="stMetric"] {
        background-color: #1e2130; padding: 20px; border-radius: 15px; border-bottom: 4px solid #00ffa2;
    }
    div[data-testid="stMetricValue"] { color: #00ffa2; font-size: 32px; }
    
    /* Estilo dos Cards de Listagem */
    .card-sistema {
        background-color: #1e2130; padding: 15px; border-radius: 10px;
        border-left: 5px solid #00ffa2; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
def get_connection():
    conn = sqlite3.connect('agrofrota_vfinal.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS pneus (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, marca TEXT, medida TEXT, qtd INTEGER, preco REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, documento TEXT, endereco TEXT, telefone TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, tipo TEXT, data TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS producao (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, pneu TEXT, servico TEXT, entrada TEXT, saida TEXT)')
    return conn

conn = get_connection()

# --- 3. BARRA LATERAL (CONFIGURAÇÕES VISUAIS) ---
with st.sidebar:
    st.subheader("⚙️ Personalização")
    nome_sistema = st.text_input("Nome da Empresa", value="AGRO-FROTA")
    logo_upload = st.file_uploader("Trocar Logotipo", type=['png', 'jpg'])
    st.write("---")

# Cabeçalho Dinâmico
if logo_upload:
    st.image(logo_upload, width=100)
else:
    st.markdown(f"<h1 style='text-align: center; color: #00ffa2;'>🚜 {nome_sistema.upper()}</h1>", unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO POR ABAS NO TOPO ---
tab_dash, tab_fin, tab_est, tab_cli, tab_prod = st.tabs([
    "📊 DASHBOARD", "💰 FINANCEIRO", "🛞 ESTOQUE", "👥 CLIENTES", "🛠️ PRODUÇÃO"
])

# --- MÓDULO: DASHBOARD ---
with tab_dash:
    df_p = pd.read_sql("SELECT tipo, qtd FROM pneus", conn)
    df_f = pd.read_sql("SELECT valor, tipo FROM financeiro", conn)
    total_cli = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'].iloc
    
    res = df_f[df_f['tipo'] == 'Receita']['valor'].sum()
    des = df_f[df_f['tipo'] == 'Despesa']['valor'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo Caixa", f"R$ {res - des:,.2f}")
    c2.metric("Pneus Estoque", int(df_p['qtd'].sum()) if not df_p.empty else 0)
    c3.metric("Clientes", total_cli)
    c4.metric("Status", "Ativo")

    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>🎯 Distribuição de Segmentos</h3>", unsafe_allow_html=True)
    if not df_p.empty:
        fig = px.pie(df_p, values='qtd', names='tipo', hole=0.5, color_discrete_sequence=['#00ffa2', '#0288d1'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- MÓDULO: ESTOQUE (COM EDIÇÃO) ---
with tab_est:
    st.subheader("🛞 Gestão de Pneus")
    with st.expander("➕ Novo Cadastro"):
        with st.form("form_est"):
            e1, e2, e3 = st.columns(3)
            tipo_e = e1.selectbox("Tipo", ["Agrícola", "Rodoviário"])
            marca_e = e2.text_input("Marca")
            med_e = e3.text_input("Medida")
            qtd_e = st.number_input("Qtd", min_value=1)
            if st.form_submit_button("Salvar Item"):
                conn.execute("INSERT INTO pneus (tipo, marca, medida, qtd) VALUES (?,?,?,?)", (tipo_e, marca_e, med_e, qtd_e))
                conn.commit()
                st.rerun()

    st.write("---")
    df_estoque = pd.read_sql("SELECT * FROM pneus", conn)
    for _, r in df_estoque.iterrows():
        cols = st.columns([4, 1])
        cols.write(f"**{r['tipo']}** - {r['marca']} ({r['medida']}) | Qtd: {r['qtd']}")
        if cols.button("🗑️", key=f"del_p_{r['id']}"):
            conn.execute(f"DELETE FROM pneus WHERE id={r['id']}")
            conn.commit()
            st.rerun()

# --- MÓDULO: CLIENTES (COM EDIÇÃO) ---
with tab_cli:
    st.subheader("👥 Fichas de Clientes")
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    
    with st.expander("📝 Cadastro / Edição de Cliente", expanded=True if st.session_state.edit_id else False):
        val = ["", "", "", ""]
        if st.session_state.edit_id:
            val = conn.execute("SELECT nome, documento, endereco, telefone FROM clientes WHERE id=?", (st.session_state.edit_id,)).fetchone()
        
        with st.form("form_cli"):
            n = st.text_input("Nome/Razão Social", value=val[0])
            d = st.text_input("CNPJ/CPF", value=val[1])
            e = st.text_input("Endereço", value=val[2])
            t = st.text_input("Telefone", value=val[3])
            if st.form_submit_button("💾 Salvar Cliente"):
                if st.session_state.edit_id:
                    conn.execute("UPDATE clientes SET nome=?, documento=?, endereco=?, telefone=? WHERE id=?", (n, d, e, t, st.session_state.edit_id))
                    st.session_state.edit_id = None
                else:
                    conn.execute("INSERT INTO clientes (nome, documento, endereco, telefone) VALUES (?,?,?,?)", (n, d, e, t))
                conn.commit(); st.rerun()

    df_cli = pd.read_sql("SELECT * FROM clientes", conn)
    for _, r in df_cli.iterrows():
        with st.container():
            st.markdown(f'<div class="card-sistema"><b>{r["nome"]}</b> - {r["documento"]}</div>', unsafe_allow_html=True)
            c1, c2, _ = st.columns([1, 1, 8])
            if c1.button("📝", key=f"ed_c_{r['id']}"): st.session_state.edit_id = r['id']; st.rerun()
            if c2.button("🗑️", key=f"de_c_{r['id']}"): conn.execute(f"DELETE FROM clientes WHERE id={r['id']}"); conn.commit(); st.rerun()

# --- MÓDULO: PRODUÇÃO ---
with tab_prod:
    st.subheader("🛠️ Ordens de Serviço")
    with st.form("form_os"):
        o1, o2 = st.columns(2)
        c_os = o1.text_input("Nome do Cliente")
        p_os = o2.text_input("Pneu/Serviço")
        if st.form_submit_button("Abrir O.S."):
            agora = datetime.now().strftime('%d/%m/%Y %H:%M')
            conn.execute("INSERT INTO producao (cliente, pneu, entrada) VALUES (?,?,?)", (c_os, p_os, agora))
            conn.commit(); st.rerun()
    
    st.write("---")
    df_prod = pd.read_sql("SELECT * FROM producao ORDER BY id DESC", conn)
    for _, r in df_prod.iterrows():
        st.markdown(f'<div class="card-sistema"><b>OS #{r["id"]} - {r["cliente"]}</b><br>Serviço: {r["pneu"]} | Entrada: {r["entrada"]}</div>', unsafe_allow_html=True)
















import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILO ---
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

# --- 2. BANCO DE DADOS E FUNÇÕES AUXILIARES ---
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

# --- 3. INTERFACE PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)

tab_dash, tab_fin, tab_est, tab_cli, tab_prod = st.tabs([
    "📊 DASHBOARD", "💰 FINANCEIRO", "🛞 ESTOQUE", "👥 CLIENTES", "🛠️ PRODUÇÃO"
])

# --- MÓDULO: DASHBOARD ---
with tab_dash:
    conn = get_connection()
    df_pneus = pd.read_sql("SELECT tipo, qtd FROM pneus", conn)
    df_fin = pd.read_sql("SELECT valor, tipo FROM financeiro", conn)
    total_cli = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'].iloc
    conn.close()

    rec = df_fin[df_fin['tipo'] == 'Receita']['valor'].sum()
    des = df_fin[df_fin['tipo'] == 'Despesa']['valor'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo em Caixa", f"R$ {rec - des:,.2f}")
    c2.metric("Pneus em Estoque", int(df_pneus['qtd'].sum()) if not df_pneus.empty else 0)
    c3.metric("Clientes Ativos", total_cli)
    c4.metric("Produtividade", "92%")

    st.markdown("---")
    if not df_pneus.empty:
        fig = px.pie(df_pneus, values='qtd', names='tipo', hole=0.5, color_discrete_sequence=['#00ffa2', '#0288d1'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# --- MÓDULO: FINANCEIRO ---
with tab_fin:
    st.subheader("💰 Gestão de Fluxo de Caixa")
    with st.form("fin_form"):
        col_f1, col_f2, col_f3 = st.columns(3)
        d_fin = col_f1.text_input("Descrição")
        v_fin = col_f2.number_input("Valor (R$)", min_value=0.0)
        t_fin = col_f3.selectbox("Tipo", ["Receita", "Despesa"])
        if st.form_submit_button("Lançar"):
            conn = get_connection()
            conn.execute("INSERT INTO financeiro (descricao, valor, tipo, data) VALUES (?,?,?,?)", 
                         (d_fin, v_fin, t_fin, datetime.now().strftime('%d/%m/%Y')))
            conn.commit()
            st.rerun()

# --- MÓDULO: ESTOQUE ---
with tab_est:
    st.subheader("🛞 Inventário de Pneus")
    with st.expander("➕ Cadastrar Pneu"):
        with st.form("pneu_form"):
            col_p1, col_p2 = st.columns(2)
            tp_p = col_p1.selectbox("Segmento", ["Agrícola", "Rodoviário"])
            ma_p = col_p2.text_input("Marca")
            me_p = st.text_input("Medida")
            qt_p = st.number_input("Quantidade", min_value=1)
            if st.form_submit_button("Salvar"):
                conn = get_connection()
                conn.execute("INSERT INTO pneus (tipo, marca, medida, qtd) VALUES (?,?,?,?)", (tp_p, ma_p, me_p, qt_p))
                conn.commit()
                st.rerun()
    
    conn = get_connection()
    df_e = pd.read_sql("SELECT * FROM pneus", conn)
    for _, r in df_e.iterrows():
        cols = st.columns([4, 1])
        cols.write(f"**{r['tipo']} {r['marca']}** - {r['medida']} (Qtd: {r['qtd']})")
        if cols.button("🗑️", key=f"del_p_{r['id']}"):
            conn.execute(f"DELETE FROM pneus WHERE id={r['id']}")
            conn.commit()
            st.rerun()
    conn.close()

# --- MÓDULO: CLIENTES (CADASTRO E EDIÇÃO) ---
with tab_cli:
    st.subheader("👥 Gestão de Clientes")
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    
    with st.expander("📝 Formulário Cliente", expanded=True if st.session_state.edit_id else False):
        v = [""] * 6
        if st.session_state.edit_id:
            conn = get_connection()
            v = conn.execute("SELECT nome, documento, endereco, telefone, email, obs FROM clientes WHERE id=?", (st.session_state.edit_id,)).fetchone()
        
        with st.form("cli_form"):
            c_c1, c_c2 = st.columns(2)
            nome = c_c1.text_input("Nome/Razão Social", value=v[0])
            doc = c_c2.text_input("CNPJ/CPF", value=v[1])
            end = st.text_input("Endereço", value=v[2])
            col_c3, col_c4 = st.columns(2)
            tel = col_c3.text_input("Telefone", value=v[3])
            mail = col_c4.text_input("E-mail", value=v[4])
            obs = st.text_area("Observações", value=v[5])
            if st.form_submit_button("💾 Salvar"):
                conn = get_connection()
                if st.session_state.edit_id:
                    conn.execute("UPDATE clientes SET nome=?, documento=?, endereco=?, telefone=?, email=?, obs=? WHERE id=?", (nome, doc, end, tel, mail, obs, st.session_state.edit_id))
                    st.session_state.edit_id = None
                else:
                    conn.execute("INSERT INTO clientes (nome, documento, endereco, telefone, email, obs) VALUES (?,?,?,?,?,?)", (nome, doc, end, tel, mail, obs))
                conn.commit()
                st.rerun()

    conn = get_connection()
    df_cl = pd.read_sql("SELECT id, nome, documento, telefone FROM clientes", conn)
    for _, r in df_cl.iterrows():
        with st.container():
            st.markdown(f'<div class="card-sistema"><b>{r["nome"]}</b><br>{r["documento"]} | {r["telefone"]}</div>', unsafe_allow_html=True)
            b1, b2, _ = st.columns([1,1,4])
            if b1.button("📝", key=f"ed_{r['id']}"): 
                st.session_state.edit_id = r['id']
                st.rerun()
            if b2.button("🗑️", key=f"de_{r['id']}"):
                conn.execute(f"DELETE FROM clientes WHERE id={r['id']}")
                conn.commit()
                st.rerun()

# --- MÓDULO: PRODUÇÃO (PDF E HORÁRIOS) ---
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

    conn = get_connection()
    df_pr = pd.read_sql("SELECT * FROM producao ORDER BY id DESC", conn)
    for _, r in df_pr.iterrows():
        st.markdown(f'<div class="card-sistema"><b>OS #{r["id"]} - {r["cliente"]}</b><br>Serviço: {r["servico"]} | Entrada: {r["entrada"]}</div>', unsafe_allow_html=True)
        o1, o2, o3 = st.columns([2,2,2])
        if not r['saida'] and o1.button("✅ Saída", key=f"sai_{r['id']}"):
            sai = datetime.now().strftime('%d/%m/%Y %H:%M')
            conn.execute(f"UPDATE producao SET saida='{sai}', status='Fim' WHERE id={r['id']}")
            conn.commit()
            st.rerun()
        pdf_d = {"OS": r['id'], "Cliente": r['cliente'], "Serviço": r['servico'], "Entrada": r['entrada'], "Saída": r['saida']}
        o2.download_button("📄 PDF", gerar_pdf_os(pdf_d), f"OS_{r['id']}.pdf", key=f"pdf_{r['id']}")
        if o3.button("🗑️", key=f"del_os_{r['id']}"):
            conn.execute(f"DELETE FROM producao WHERE id={r['id']}")
            conn.commit()
            st.rerun()
    conn.close()













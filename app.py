import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

# 2. FUNÇÕES DE BANCO DE DADOS (SQLite)
def get_connection():
    return sqlite3.connect('agrofrota_vfinal.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pneus 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, marca TEXT, medida TEXT, qtd INTEGER, preco REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, documento TEXT, cidade TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. ESTILIZAÇÃO CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffa2; }
    .card { background-color: #1e2130; padding: 20px; border-radius: 15px; border-left: 5px solid #00ffa2; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #00ffa2; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)
    st.write("---")
    menu = st.selectbox("Navegação", ["📊 Dashboard", "🛞 Estoque Pneus", "👥 Clientes", "🛠️ Produção"])

# 5. MÓDULO: DASHBOARD
if menu == "📊 Dashboard":
    st.title("🚀 Painel de Controle")
    
    conn = get_connection()
    # Puxando dados reais e tratando se estiver vazio
    resumo = pd.read_sql("SELECT SUM(qtd) as total, SUM(qtd * preco) as valor FROM pneus", conn)
    total_pneus = int(resumo['total'].iloc[0] or 0)
    valor_total = float(resumo['valor'].iloc[0] or 0.0)
    total_cli = int(pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'].iloc[0])
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valor Estoque", f"R$ {valor_total:,.2f}")
    col2.metric("Qtd Pneus", total_pneus)
    col3.metric("Clientes", total_cli)
    col4.metric("Status", "Ativo")

    st.write("---")
    st.subheader("📈 Movimentação Mensal")
    # Números corrigidos (sem zeros à esquerda para evitar erro de sintaxe)
    chart_data = pd.DataFrame({'Mês': ['Jan', 'Fev', 'Mar'], 'Vendas': [10, 25, 18]})
    st.line_chart(chart_data.set_index('Mês'))

# 6. MÓDULO: ESTOQUE
elif menu == "🛞 Estoque Pneus":
    st.title("🛞 Gestão de Estoque")
    with st.form("add_pneu", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        t = c1.selectbox("Tipo", ["Agrícola", "Rodoviário"])
        m = c2.text_input("Marca")
        med = c3.text_input("Medida")
        c4, c5 = st.columns(2)
        q = c4.number_input("Qtd", min_value=1, step=1)
        p = c5.number_input("Preço Unitário", min_value=0.0)
        
        if st.form_submit_button("➕ Salvar Pneu"):
            conn = get_connection()
            conn.execute("INSERT INTO pneus (tipo, marca, medida, qtd, preco) VALUES (?,?,?,?,?)", (t, m, med, q, p))
            conn.commit()
            conn.close()
            st.success("Cadastrado!")
            st.rerun()

    st.subheader("Itens em Estoque")
    conn = get_connection()
    df = pd.read_sql("SELECT tipo, marca, medida, qtd, preco FROM pneus", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

# 7. MÓDULO: CLIENTES
elif menu == "👥 Clientes":
    st.title("👥 Clientes")
    with st.expander("Novo Cliente"):
        n = st.text_input("Nome")
        d = st.text_input("CPF/CNPJ")
        c = st.text_input("Cidade")
        if st.button("Cadastrar"):
            conn = get_connection()
            conn.execute("INSERT INTO clientes (nome, documento, cidade) VALUES (?,?,?)", (n, d, c))
            conn.commit()
            conn.close()
            st.rerun()

    conn = get_connection()
    df_c = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()
    for _, row in df_c.iterrows():
        st.markdown(f'<div class="card"><b>{row["nome"]}</b><br>{row["documento"]} | {row["cidade"]}</div>', unsafe_allow_html=True)

# 8. MÓDULO: PRODUÇÃO (COM PDF)
elif menu == "🛠️ Produção":
    st.title("🛠️ Ficha de Produção")
    conn = get_connection()
    lista_cli = pd.read_sql("SELECT nome FROM clientes", conn)['nome'].tolist()
    conn.close()
    
    if lista_cli:
        with st.form("gera_ficha"):
            sel_cli = st.selectbox("Cliente", lista_cli)
            servs = st.multiselect("Serviços", ["Recapagem", "Montagem", "Vulcanização"])
            obs = st.text_area("Dados do Pneu")
            if st.form_submit_button("Gerar Ficha"):
                # Geração simples de PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "FICHA DE PRODUÇÃO - AGROFROTA", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.ln(10)
                pdf.cell(0, 10, f"Cliente: {sel_cli}", ln=True)
                pdf.cell(0, 10, f"Serviços: {', '.join(servs)}", ln=True)
                pdf.multi_cell(0, 10, f"Obs: {obs}")
                
                pdf_output = pdf.output()
                st.download_button(label="📥 Baixar Ficha PDF", data=pdf_output, file_name="ficha.pdf", mime="application/pdf")
    else:
        st.warning("Cadastre um cliente primeiro.")




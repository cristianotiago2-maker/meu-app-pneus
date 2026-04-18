import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

# 2. BANCO DE DADOS
def get_connection():
    return sqlite3.connect('agrofrota_vfinal.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS pneus (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, marca TEXT, medida TEXT, qtd INTEGER, preco REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, documento TEXT, cidade TEXT)')
    conn.commit()
    conn.close()

init_db()

# 3. O VISUAL "TOP" (CSS PARA CARDS ESCUROS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    div[data-testid="stMetricValue"] { font-size: 32px; color: #00ffa2; font-weight: bold; }
    .card {
        background-color: #1e2130;
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #00ffa2;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: white !important; }
    .stButton>button { background-color: #00ffa2; color: black; border-radius: 10px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# 4. MENU LATERAL (IDENTIDADE VISUAL)
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00ffa2;'>AGRO-FROTA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Gestão Empresarial Profissional</p>", unsafe_allow_html=True)
    st.write("---")
    menu = st.selectbox("Módulos", ["Dashboard", "Estoque de Pneus", "Clientes", "Produção"])
    st.write("---")
    st.caption("v1.2 - Sistema Estável")

# 5. MÓDULO: DASHBOARD (VISUAL DA PRIMEIRA IMAGEM)
if menu == "Dashboard":
    st.subheader("📊 Resumo do Negócio")
    
    conn = get_connection()
    resumo = pd.read_sql("SELECT SUM(qtd) as total, SUM(qtd * preco) as valor FROM pneus", conn)
    total_pneus = int(resumo['total'].iloc[0] or 0)
    total_cli = int(pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'].iloc[0])
    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pneus em Estoque", total_pneus)
    with col2:
        st.metric("Clientes Ativos", total_cli)
    with col3:
        st.metric("Status Produção", "88%", "+5%")

    st.write("---")
    st.subheader("📈 Fluxo de Operações")
    # Números corrigidos (sem zeros à esquerda: usei 8, 12, 25)
    dados = pd.DataFrame({'Mes': ['Jan', 'Fev', 'Mar'], 'Movimento': [10, 25, total_pneus if total_pneus > 0 else 5]})
    st.area_chart(dados.set_index('Mes'))

# 6. MÓDULO: ESTOQUE (CADASTRO TÉCNICO)
elif menu == "Estoque de Pneus":
    st.subheader("🛞 Gestão de Pneus Agrícolas e Rodoviários")
    
    with st.container():
        st.markdown('<div class="card"><b>Novo Cadastro</b></div>', unsafe_allow_html=True)
        with st.form("pneu_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            tipo = c1.selectbox("Tipo de Pneu", ["Agrícola", "Rodoviário"])
            marca = c2.text_input("Marca")
            medida = c3.text_input("Medida")
            
            c4, c5 = st.columns(2)
            qtd = c4.number_input("Quantidade", min_value=1, step=1)
            preco = c5.number_input("Preço de Custo (R$)", min_value=0.0)
            
            if st.form_submit_button("Salvar no Estoque"):
                conn = get_connection()
                conn.execute("INSERT INTO pneus (tipo, marca, medida, qtd, preco) VALUES (?,?,?,?,?)", (tipo, marca, medida, qtd, preco))
                conn.commit()
                conn.close()
                st.success("Item adicionado com sucesso!")
                st.rerun()

    st.write("---")
    conn = get_connection()
    df_pneus = pd.read_sql("SELECT tipo, marca, medida, qtd FROM pneus", conn)
    conn.close()
    st.table(df_pneus)

# 7. MÓDULO: PRODUÇÃO (GERADOR DE FICHA PDF)
elif menu == "Produção":
    st.subheader("🛠️ Ficha de Produção")
    
    conn = get_connection()
    cli_list = pd.read_sql("SELECT nome FROM clientes", conn)['nome'].tolist()
    conn.close()
    
    if cli_list:
        with st.form("ficha"):
            cliente = st.selectbox("Selecionar Cliente", cli_list)
            servicos = st.multiselect("Serviços", ["Montagem", "Recapagem", "Vulcanização", "Balanceamento"])
            obs = st.text_area("Observações Técnicas (Nº Série, Sulco, etc.)")
            
            if st.form_submit_button("Gerar Documento"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "AGRO-FROTA - FICHA DE PRODUÇÃO", ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Cliente: {cliente}", ln=True)
                pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
                pdf.cell(0, 10, f"Serviços: {', '.join(servicos)}", ln=True)
                pdf.ln(5)
                pdf.multi_cell(0, 10, f"Observações: {obs}")
                
                st.download_button("📥 Baixar PDF", pdf.output(), "ficha.pdf", "application/pdf")
    else:
        st.warning("Cadastre um cliente antes de abrir uma produção.")

# 8. MÓDULO: CLIENTES (LISTA EM CARDS)
elif menu == "Clientes":
    st.subheader("👥 Cadastro de Clientes")
    with st.expander("➕ Adicionar Novo"):
        n = st.text_input("Nome/Empresa")
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






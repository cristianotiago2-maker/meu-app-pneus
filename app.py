

(sem assunto)
Caixa de entrada

Tiago Cristiano da Silva <cristianotiago2@gmail.com>
08:29 (há 0 minuto)
para mim

import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

# --- CONFIGURAÇÃO E BANCO ---
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

def get_connection():
    return sqlite3.connect('agrofrota_v4.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS pneus (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, marca TEXT, medida TEXT, qtd INTEGER, preco REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, documento TEXT, cidade TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_pdf_ficha(cliente, servicos, detalhes):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AGRO-FROTA GESTÃO EMPRESARIAL", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Ficha de Produção - {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.line(10, 35, 200, 35)
    
    # Dados do Cliente
    pdf.ln(15)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Cliente: {cliente}", ln=True)
    
    # Serviços
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Serviços Solicitados:", ln=True)
    pdf.set_font("Arial", "", 12)
    for s in servicos:
        pdf.cell(0, 10, f"- {s}", ln=True)
    
    # Detalhes
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detalhes Técnicos:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, detalhes)
    
    # Rodapé/Assinatura
    pdf.ln(20)
    pdf.line(10, pdf.get_y(), 80, pdf.get_y())
    pdf.cell(0, 10, "Assinatura do Técnico", ln=True)
    
    return pdf.output()

# --- INTERFACE (MANTENDO O VISUAL) ---
st.markdown("<style>.card { background-color: #1e2130; padding: 20px; border-radius: 15px; border-left: 5px solid #00ffa2; margin-bottom: 10px; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)
    menu = st.selectbox("Navegação", ["📊 Dashboard", "🛞 Estoque Pneus", "👥 Clientes", "🛠️ Produção"])

# --- MÓDULO PRODUÇÃO (FOCO NA FICHA) ---
if menu == "🛠️ Produção":
    st.title("🛠️ Gerar Ficha de Produção")
    
    conn = get_connection()
    clientes_df = pd.read_sql("SELECT nome FROM clientes", conn)
    conn.close()
    
    if not clientes_df.empty:
        with st.form("ficha_prod"):
            sel_cli = st.selectbox("Selecione o Cliente", clientes_df['nome'].tolist())
            servs = st.multiselect("Serviços", ["Recapagem", "Montagem", "Vulcanização", "Alinhamento"])
            obs = st.text_area("Descrição do Pneu (Marca, Medida, Série)")
            
            submetido = st.form_submit_button("✅ Preparar Ficha")
            
            if submetido:
                st.session_state.pdf_pronto = True
                st.session_state.dados_ficha = {"cli": sel_cli, "serv": servs, "obs": obs}

        if "pdf_pronto" in st.session_state:
            pdf_bytes = gerar_pdf_ficha(
                st.session_state.dados_ficha["cli"],
                st.session_state.dados_ficha["serv"],
                st.session_state.dados_ficha["obs"]
            )
            
            st.download_button(
                label="📥 Baixar Ficha em PDF",
                data=pdf_bytes,
                file_name=f"ficha_{st.session_state.dados_ficha['cli']}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Cadastre um cliente antes de gerar fichas.")

# --- OUTROS MÓDULOS (SIMPLIFICADOS PARA O EXEMPLO) ---
elif menu == "📊 Dashboard":
    st.title("🚀 Dashboard")
    st.info("Utilize os módulos de estoque e clientes para popular os dados.")
elif menu == "🛞 Estoque Pneus":
    st.title("🛞 Estoque")
    # ... (mesmo código anterior de estoque)
elif menu == "👥 Clientes":
    st.title("👥 Clientes")
    # ... (mesmo código anterior de clientes)


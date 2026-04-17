import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página e Estilo
st.set_page_config(page_title="VULCAT PNEUS - Gestão Pro", layout="wide", page_icon="🚛")

# Estilo Visual (Cores e Bordas)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO PARA GERAR PDF ---
def exportar_pdf(titulo, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, f"VULCAT PNEUS - {titulo}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    # Cabeçalho
    for col in df.columns:
        pdf.cell(31, 8, str(col), border=1)
    pdf.ln()
    # Linhas
    for i in range(len(df)):
        for col in df.columns:
            pdf.cell(31, 8, str(df.iloc[i][col])[:15], border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INICIALIZAÇÃO DOS DADOS ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'clientes': pd.DataFrame(columns=['Nome', 'CNPJ/CPF', 'Telefone', 'Endereco']),
        'medidas': pd.DataFrame({
            "Medida": ["295/80 R22.5", "18.4-34", "11.00 R22", "14.9-24", "12.4-24", "23.1-26"],
            "Tipo": ["Rodoviário", "Agrícola", "Rodoviário", "Agrícola", "Agrícola", "Agrícola"]
        }),
        'producao': pd.DataFrame(columns=['ID', 'Cliente', 'Serviço', 'Entrada', 'Saída', 'Status', 'Anotações']),
        'financeiro': pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor']),
        'estoque': pd.DataFrame({"Item": ["Manchão G", "Cola 1L", "Borracha"], "Qtd": [10, 5, 20]})
    }

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    st.divider()
    menu = st.radio("MENU", ["📊 Painel Geral", "👥 Clientes", "📏 Medidas", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro"])
    st.divider()
    emp_nome = st.text_input("Empresa", "Vulcat Pneus")
    emp_tel = st.text_input("Telefone", "(00) 00000-0000")

# --- 📊 PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title(f"📊 Painel Geral - {emp_nome}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Serviços Ativos", len(st.session_state.db['producao']))
    receita = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    c2.metric("Faturamento Mensal", f"R$ {receita:,.2f}")
    c3.metric("Estoque Crítico", len(st.session_state.db['estoque'][st.session_state.db['estoque']['Qtd'] < 5]))
    
    st.divider()
    st.subheader("🏭 Fluxo da Oficina")
    st.dataframe(st.session_state.db['producao'], use_container_width=True)

# --- 👥 CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    st.session_state.db['clientes'] = st.data_editor(st.session_state.db['clientes'], num_rows="dynamic", use_container_width=True)

# --- 📏 MEDIDAS ---
elif menu == "📏 Medidas":
    st.header("📏 Catálogo de Medidas")
    st.session_state.db['medidas'] = st.data_editor(st.session_state.db['medidas'], num_rows="dynamic", use_container_width=True)

# --- 📝 ORÇAMENTOS ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    if st.session_state.db['clientes'].empty:
        st.warning("⚠️ Cadastre um cliente primeiro na aba Clientes.")
    else:
        with st.form("orc"):
            c_sel = st.selectbox("Cliente", st.session_state.db['clientes']['Nome'].tolist())
            m_sel = st.selectbox("Medida", st.session_state.db['medidas']['Medida'].tolist())
            serv = st.text_input("Serviço")
            val = st.number_input("Valor R$", min_value=0.0)
            if st.form_submit_button("🚀 Aprovar e Iniciar"):
                id_serv = len(st.session_state.db['producao']) + 1
                hora = datetime.now().strftime("%H:%M")
                # Produção
                np = pd.DataFrame([[id_serv, c_sel, f"{m_sel} - {serv}", hora, "--:--", "Fila", ""]], columns=st.session_state.db['producao'].columns)
                st.session_state.db['producao'] = pd.concat([st.session_state.db['producao'], np], ignore_index=True)
                # Financeiro
                nf = pd.DataFrame([[datetime.now().strftime("%d/%m"), f"OS {id_serv}: {c_sel}", "Entrada", val]], columns=st.session_state.db['financeiro'].columns)
                st.session_state.db['financeiro'] = pd.concat([st.session_state.db['financeiro'], nf], ignore_index=True)
                st.success("✅ OS Criada! Verifique Produção e Financeiro.")

# --- 🏭 PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção")
    st.session_state.db['producao'] = st.data_editor(st.session_state.db['producao'], num_rows="dynamic", use_container_width=True)
    if not st.session_state.db['producao'].empty:
        pdf = exportar_pdf("PRODUÇÃO", st.session_state.db['producao'])
        st.download_button("📥 Baixar PDF Produção", pdf, "producao.pdf", "application/pdf")

# --- 📦 ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque")
    st.session_state.db['estoque'] = st.data_editor(st.session_state.db['estoque'], num_rows="dynamic", use_container_width=True)
    pdf = exportar_pdf("ESTOQUE", st.session_state.db['estoque'])
    st.download_button("📥 Baixar PDF Estoque", pdf, "estoque.pdf", "application/pdf")

# --- 💰 FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Financeiro")
    st.session_state.db['financeiro'] = st.data_editor(st.session_state.db['financeiro'], num_rows="dynamic", use_container_width=True)
    pdf = exportar_pdf("FINANCEIRO", st.session_state.db['financeiro'])
    st.download_button("📥 Baixar PDF Financeiro", pdf, "financeiro.pdf", "application/pdf")




 


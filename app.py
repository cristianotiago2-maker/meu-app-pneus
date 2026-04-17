import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="VULCAT PNEUS - Gestão PDF", layout="wide", page_icon="🚛")

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_pdf(titulo, colunas, dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=f"VULCAT PNEUS - {titulo}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    # Cabeçalho da tabela
    pdf.set_font("Arial", "B", 10)
    for col in colunas:
        pdf.cell(38, 10, str(col), border=1)
    pdf.ln()
    
    # Dados da tabela
    pdf.set_font("Arial", size=9)
    for index, row in dados.iterrows():
        for item in row:
            pdf.cell(38, 10, str(item)[:20], border=1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INICIALIZAÇÃO DO BANCO ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'clientes': pd.DataFrame(columns=['Nome', 'CNPJ/CPF', 'Telefone', 'Endereço']),
        'medidas': pd.DataFrame({"Medida": ["295/80 R22.5", "18.4-34", "11.00 R22"], "Tipo": ["Rodoviário", "Agrícola", "Rodoviário"]}),
        'producao': pd.DataFrame(columns=['ID', 'Cliente', 'Medida', 'Serviço', 'Entrada', 'Saída', 'Status']),
        'financeiro': pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor']),
        'estoque': pd.DataFrame({"Item": ["Manchão G", "Cola 1L"], "Qtd": [10, 5]})
    }

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel Geral", "👥 Clientes", "📏 Medidas", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro"])

# --- 1. PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title("📊 Painel Geral")
    st.subheader("📋 Resumo da Produção")
    st.dataframe(st.session_state.db['producao'], use_container_width=True)
    if not st.session_state.db['producao'].empty:
        pdf_prod = gerar_pdf("RESUMO PRODUÇÃO", st.session_state.db['producao'].columns, st.session_state.db['producao'])
        st.download_button("📥 Baixar PDF Produção", pdf_prod, "producao_vulcat.pdf", "application/pdf")

# --- 2. CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Clientes")
    st.session_state.db['clientes'] = st.data_editor(st.session_state.db['clientes'], num_rows="dynamic", use_container_width=True)

# --- 3. MEDIDAS ---
elif menu == "📏 Medidas":
    st.header("📏 Medidas")
    st.session_state.db['medidas'] = st.data_editor(st.session_state.db['medidas'], num_rows="dynamic", use_container_width=True)

# --- 4. ORÇAMENTOS ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    with st.form("orc"):
        cli = st.selectbox("Cliente", st.session_state.db['clientes']['Nome'].tolist()) if not st.session_state.db['clientes'].empty else st.text_input("Nome do Cliente (Cadastre antes)")
        med = st.selectbox("Medida", st.session_state.db['medidas']['Medida'].tolist())
        serv = st.text_input("Serviço")
        val = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("🚀 Aprovar e Gerar PDF"):
            id_os = len(st.session_state.db['producao']) + 1
            np = pd.DataFrame([[id_os, cli, med, serv, datetime.now().strftime("%H:%M"), "--:--", "Fila"]], columns=st.session_state.db['producao'].columns)
            st.session_state.db['producao'] = pd.concat([st.session_state.db['producao'], np], ignore_index=True)
            nf = pd.DataFrame([[datetime.now().strftime("%d/%m"), f"OS {id_os}: {cli}", "Entrada", val]], columns=st.session_state.db['financeiro'].columns)
            st.session_state.db['financeiro'] = pd.concat([st.session_state.db['financeiro'], nf], ignore_index=True)
            st.success("Orçamento Aprovado!")

# --- 5. PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção")
    st.session_state.db['producao'] = st.data_editor(st.session_state.db['producao'], num_rows="dynamic", use_container_width=True)
    pdf_p = gerar_pdf("FICHA DE PRODUÇÃO", st.session_state.db['producao'].columns, st.session_state.db['producao'])
    st.download_button("📥 Baixar Ficha de Produção (PDF)", pdf_p, "ficha_oficina.pdf", "application/pdf")

# --- 6. ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque")
    st.session_state.db['estoque'] = st.data_editor(st.session_state.db['estoque'], num_rows="dynamic", use_container_width=True)
    pdf_e = gerar_pdf("INVENTÁRIO ESTOQUE", st.session_state.db['estoque'].columns, st.session_state.db['estoque'])
    st.download_button("📥 Baixar Estoque (PDF)", pdf_e, "estoque_vulcat.pdf", "application/pdf")

# --- 7. FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Financeiro")
    st.session_state.db['financeiro'] = st.data_editor(st.session_state.db['financeiro'], num_rows="dynamic", use_container_width=True)
    pdf_f = gerar_pdf("RELATÓRIO FINANCEIRO", st.session_state.db['financeiro'].columns, st.session_state.db['financeiro'])
    st.download_button("📥 Baixar Relatório Mensal (PDF)", pdf_f, "financeiro_vulcat.pdf", "application/pdf")


 


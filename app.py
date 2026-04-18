import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Vulcat Pneus PRO", page_icon="🛞", layout="wide")

# 2. CLASSE PARA GERAR PDF PERSONALIZADO
class VulcatPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "VULCAT PNEUS - SISTEMA DE GESTÃO", ln=True, align="C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 5, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
        self.ln(10)

def exportar_tabela_pdf(titulo, colunas, dados):
    pdf = VulcatPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, titulo.upper(), ln=True)
    pdf.ln(5)
    
    # Cabeçalho da Tabela
    pdf.set_font("Arial", "B", 10)
    for col in colunas:
        pdf.cell(45, 8, col, 1)
    pdf.ln()
    
    # Dados
    pdf.set_font("Arial", "", 10)
    for row in dados:
        for item in row:
            pdf.cell(45, 8, str(item), 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', 'replace')

# 3. SIDEBAR (DADOS DA EMPRESA)
with st.sidebar:
    st.header("🏢 Configuração")
    logo_url = st.text_input("Link do Logo", "https://flaticon.com")
    if logo_url: st.image(logo_url, width=150)
    nome_empresa = st.text_input("Empresa", "VULCAT PNEUS")
    cnpj = st.text_input("CNPJ", "00.000.000/0001-00")

# 4. DASHBOARD (PAINEL GERAL)
st.title(f"🚜 {nome_empresa}")
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "💰 Financeiro", "📦 Estoque", "👥 Clientes"])

# --- ABA 1: ORÇAMENTO ---
with tabs[0]:
    st.subheader("Orçamento Formal")
    df_orc = pd.DataFrame([{"Item": "Pneu 295/80", "Qtd": 1, "Preço": 450.00}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True, key="o")
    if st.button("📥 Baixar PDF Orçamento"):
        pdf = exportar_tabela_pdf("Orçamento ao Cliente", edit_orc.columns, edit_orc.values)
        st.download_button("Clique para Salvar PDF", pdf, "orcamento.pdf", "application/pdf")

# --- ABA 2: PRODUÇÃO ---
with tabs[1]:
    st.subheader("Ficha de Oficina (Sem Valores)")
    df_prod = pd.DataFrame([{"OS": "101", "Pneu": "Série X", "Status": "Raspagem"}])
    edit_prod = st.data_editor(df_prod, num_rows="dynamic", use_container_width=True, key="p")
    if st.button("📥 Baixar Ficha de Oficina"):
        pdf = exportar_tabela_pdf("Ficha de Produção", edit_prod.columns, edit_prod.values)
        st.download_button("Clique para Salvar Ficha", pdf, "producao.pdf", "application/pdf")

# --- ABA 3: FINANCEIRO ---
with tabs[2]:
    st.subheader("Fluxo de Caixa")
    df_fin = pd.DataFrame([{"Data": "18/04", "Tipo": "Entrada", "Valor": 0.0}])
    edit_fin = st.data_editor(df_fin, num_rows="dynamic", use_container_width=True, key="f")
    if st.button("📥 Baixar Relatório Financeiro"):
        pdf = exportar_tabela_pdf("Relatório Financeiro", edit_fin.columns, edit_fin.values)
        st.download_button("Clique para Salvar Relatório", pdf, "financeiro.pdf", "application/pdf")

# --- ABA 4: ESTOQUE ---
with tabs[3]:
    st.subheader("Controle de Estoque")
    df_est = pd.DataFrame([{"Item": "Cola", "Qtd": 10}])
    edit_est = st.data_editor(df_est, num_rows="dynamic", use_container_width=True, key="e")
    if st.button("📥 Baixar Lista de Estoque"):
        pdf = exportar_tabela_pdf("Relatório de Estoque", edit_est.columns, edit_est.values)
        st.download_button("Clique para Salvar Estoque", pdf, "estoque.pdf", "application/pdf")

# --- ABA 5: CLIENTES ---
with tabs[4]:
    st.subheader("Cadastro de Clientes")
    df_cli = pd.DataFrame([{"Nome": "João Silva", "Telefone": "00-0000"}])
    edit_cli = st.data_editor(df_cli, num_rows="dynamic", use_container_width=True, key="c")
    if st.button("📥 Baixar Lista de Clientes"):
        pdf = exportar_tabela_pdf("Lista de Clientes", edit_cli.columns, edit_cli.values)
        st.download_button("Clique para Salvar Contatos", pdf, "clientes.pdf", "application/pdf")










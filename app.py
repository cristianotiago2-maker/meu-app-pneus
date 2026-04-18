import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="VULCAT PNEUS - PRO", layout="wide", page_icon="🛞")

# 2. INICIALIZAÇÃO DA MEMÓRIA (FAZ AS ABAS SE COMUNICAREM)
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone", "Endereço"])
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = pd.DataFrame(columns=["Medida", "Preço Base"])
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])

# 3. FUNÇÃO PARA GERAR PDF REAL (COM LINHA DE ASSINATURA)
def gerar_pdf_orcamento(empresa, cliente_dados, itens, total, pagto, datas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, empresa['nome'].upper(), ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"CNPJ: {empresa['cnpj']} | Tel: {empresa['tel']}", ln=True, align="C")
    pdf.cell(0, 5, empresa['end'], ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "DADOS DO CLIENTE", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Nome: {cliente_dados['nome']}", ln=True)
    pdf.cell(0, 7, f"CPF/CNPJ: {cliente_dados['doc']} | Tel: {cliente_dados['tel']}", ln=True)
    pdf.cell(0, 7, f"Endereço: {cliente_dados['end']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, f"Entrada: {datas['ent']} | Previsão Saída: {datas['sai']}", ln=True)
    pdf.ln(5)

    # Tabela de Itens
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 8, "Item/Medida", 1)
    pdf.cell(30, 8, "Qtd", 1)
    pdf.cell(40, 8, "V. Unit (R$)", 1)
    pdf.cell(40, 8, "Subtotal", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for _, row in itens.iterrows():
        sub = row['Qtd'] * row['V. Unit.']
        pdf.cell(80, 8, str(row['Item/Medida']), 1)
        pdf.cell(30, 8, str(row['Qtd']), 1)
        pdf.cell(40, 8, f"{row['V. Unit.']:,.2f}", 1)
        pdf.cell(40, 8, f"{sub:,.2f}", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL DO ORÇAMENTO: R$ {total:,.2f}", ln=True, align="R")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Forma de Pagamento: {pagto}", ln=True)

    pdf.ln(20)
    pdf.cell(0, 10, "________________________________________________", ln=True, align="C")
    pdf.cell(0, 5, "Assinatura do Cliente", ln=True, align="C")
    
    return pdf.output(dest='S')

# 4. SIDEBAR
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÃO")
    logo_file = st.file_uploader("Logo da Empresa", type=['png', 'jpg'])
    nome_empresa = st.text_input("Empresa", "VULCAT PNEUS")
    cnpj = st.text_input("CNPJ")
    tel_empresa = st.text_input("Telefone")
    end_empresa = st.text_area("Endereço")
    empresa_info = {'nome': nome_empresa, 'cnpj': cnpj, 'tel': tel_empresa, 'end': end_empresa}

# 5. ABAS
tabs = st.tabs(["📊 Dashboard", "📄 Orçamento", "🛠️ Produção", "🛞 Catálogo", "💰 Financeiro", "👥 Clientes"])

# --- ABA CLIENTES (ALIMENTA O ORÇAMENTO) ---
with tabs[5]:
    st.subheader("👥 Cadastro de Clientes")
    st.session_state.clientes = st.data_editor(st.session_state.clientes, num_rows="dynamic", use_container_width=True)

# --- ABA CATÁLOGO (ALIMENTA O ORÇAMENTO) ---
with tabs[3]:
    st.subheader("🛞 Catálogo de Medidas")
    st.session_state.catalogo = st.data_editor(st.session_state.catalogo, num_rows="dynamic", use_container_width=True)

# --- ABA ORÇAMENTO (COMUNICA COM AS OUTRAS) ---
with tabs[1]:
    st.subheader("📝 Novo Orçamento Profissional")
    
    col_c1, col_c2 = st.columns(2)
    # Aqui ele busca os nomes cadastrados na aba Clientes
    lista_clientes = st.session_state.clientes['Nome'].tolist()
    cliente_sel = col_c1.selectbox("Selecionar Cliente Cadastrado", [""] + lista_clientes)
    
    # Preenchimento automático dos dados do cliente
    cliente_doc, cliente_tel, cliente_end = "", "", ""
    if cliente_sel:
        row = st.session_state.clientes[st.session_state.clientes['Nome'] == cliente_sel].iloc[0]
        cliente_doc, cliente_tel, cliente_end = row['CPF/CNPJ'], row['Telefone'], row['Endereço']
    
    # Datas em Português
    d_ent = col_c2.date_input("Data de Entrada", format="DD/MM/YYYY")
    d_sai = col_c2.date_input("Previsão de Saída", format="DD/MM/YYYY")

    st.write(f"**Documento:** {cliente_doc} | **Tel:** {cliente_tel}")
    st.write(f"**Endereço:** {cliente_end}")

    df_orc = pd.DataFrame([{"Item/Medida": "", "Qtd": 1, "V. Unit.": 0.0}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True)
    
    total = (edit_orc['Qtd'] * edit_orc['V. Unit.']).sum()
    pagto = st.selectbox("Pagamento", ["PIX", "Dinheiro", "Boleto", "Cartão"])

    if st.button("🚀 Gerar PDF Oficial"):
        cliente_dados = {'nome': cliente_sel, 'doc': cliente_doc, 'tel': cliente_tel, 'end': cliente_end}
        datas_format = {'ent': d_ent.strftime('%d/%m/%Y'), 'sai': d_sai.strftime('%d/%m/%Y')}
        
        pdf_out = gerar_pdf_orcamento(empresa_info, cliente_dados, edit_orc, total, pagto, datas_format)
        st.download_button("📥 Baixar Arquivo PDF", data=pdf_out, file_name=f"Orcamento_{cliente_sel}.pdf", mime="application/pdf")

# --- ABA FINANCEIRO (ENTRADA/SAÍDA) ---
with tabs[4]:
    st.subheader("💰 Fluxo de Caixa")
    st.session_state.financeiro = st.data_editor(st.session_state.financeiro, num_rows="dynamic", use_container_width=True, column_config={
        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Entrada", "Saída"])
    })
    ent = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == "Saída"]['Valor'].sum()
    st.metric("Saldo Líquido", f"R$ {(ent-sai):,.2f}")

# --- ABA DASHBOARD (GRÁFICO DE PIZZA) ---
with tabs[0]:
    st.subheader("📈 Painel Geral")
    c1, c2 = st.columns(2)
    
    # Gráfico Financeiro
    fig_fin = px.pie(values=[ent, sai], names=["Entradas", "Saídas"], title="Saúde Financeira", hole=0.4, color_discrete_sequence=['#2ecc71', '#e74c3c'])
    c1.plotly_chart(fig_fin, use_container_width=True)
    
    # Gráfico de Clientes por Cidade (Exemplo de comunicação)
    c2.metric("Total de Clientes", len(st.session_state.clientes))
    c2.metric("Itens no Catálogo", len(st.session_state.catalogo))













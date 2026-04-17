import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="VULCAT PNEUS - Gestão Pro", layout="wide", page_icon="🚛")

# --- FUNÇÃO PARA GERAR PDF (SIMPLIFICADA) ---
def exportar_pdf(titulo, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"VULCAT PNEUS - {titulo}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for col in df.columns:
        pdf.cell(30, 8, str(col), border=1)
    pdf.ln()
    for i in range(len(df)):
        for col in df.columns:
            pdf.cell(30, 8, str(df.iloc[i][col])[:15], border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INICIALIZAÇÃO DOS DADOS ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'clientes': pd.DataFrame(columns=['Nome', 'CNPJ', 'Telefone', 'Endereco']),
        'medidas': pd.DataFrame({
            "Medida": ["295/80 R22.5", "18.4-34", "11.00 R22", "14.9-24", "12.4-24", "23.1-26"],
            "Tipo": ["Rodoviário", "Agrícola", "Rodoviário", "Agrícola", "Agrícola", "Agrícola"]
        }),
        'producao': pd.DataFrame(columns=['ID', 'Cliente', 'Serviço', 'Entrada', 'Saída', 'Status', 'Anotações']),
        'financeiro': pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor']),
        'estoque': pd.DataFrame({"Item": ["Manchão", "Cola", "Borracha"], "Qtd":})
    }

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    st.subheader("Configurações da Empresa")
    emp_nome = st.text_input("Nome da Empresa", "Vulcat Pneus")
    emp_cnpj = st.text_input("CNPJ", "00.000.000/0001-00")
    emp_tel = st.text_input("Telefone", "(00) 00000-0000")
    st.divider()
    menu = st.radio("MENU PRINCIPAL", ["📊 Painel Geral", "👥 Clientes", "📏 Medidas", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro"])

# --- 📊 PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title(f"📊 Painel Geral - {emp_nome}")
    
    # Métricas Coloridas
    c1, c2, c3 = st.columns(3)
    c1.metric("Serviços em Aberto", len(st.session_state.db['producao']))
    receita = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    c2.metric("Faturamento Mensal", f"R$ {receita:,.2f}", delta="Crescimento")
    c3.metric("Clientes Ativos", len(st.session_state.db['clientes']))

    st.divider()
    st.subheader("🏭 Produção em Tempo Real")
    st.dataframe(st.session_state.db['producao'], use_container_width=True)

# --- 👥 CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    st.session_state.db['clientes'] = st.data_editor(st.session_state.db['clientes'], num_rows="dynamic", use_container_width=True)

# --- 📏 MEDIDAS ---
elif menu == "📏 Medidas":
    st.header("📏 Catálogo de Medidas (Editável)")
    st.session_state.db['medidas'] = st.data_editor(st.session_state.db['medidas'], num_rows="dynamic", use_container_width=True)

# --- 📝 ORÇAMENTOS (INTEGRAÇÃO TOTAL) ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        cli = col1.selectbox("Selecione o Cliente", st.session_state.db['clientes']['Nome'].tolist() if not st.session_state.db['clientes'].empty else ["Nenhum Cliente"])
        med = col2.selectbox("Selecione a Medida", st.session_state.db['medidas']['Medida'].tolist())
        serv = st.text_input("Descrição do Serviço")
        val = st.number_input("Valor (R$)", min_value=0.0)
        
        if st.button("🚀 Aprovar: Enviar para Produção e Financeiro"):
            id_serv = len(st.session_state.db['producao']) + 1
            # 1. Produção
            nova_p = pd.DataFrame([[id_serv, cli, f"{med} - {serv}", datetime.now().strftime("%H:%M"), "--:--", "Fila", ""]], columns=st.session_state.db['producao'].columns)
            st.session_state.db['producao'] = pd.concat([st.session_state.db['producao'], nova_p], ignore_index=True)
            # 2. Financeiro
            nova_f = pd.DataFrame([[datetime.now().strftime("%d/%m"), f"OS {id_serv}: {cli}", "Entrada", val]], columns=st.session_state.db['financeiro'].columns)
            st.session_state.db['financeiro'] = pd.concat([st.session_state.db['financeiro'], nova_f], ignore_index=True)
            st.success("Sucesso! O serviço já está na oficina e o valor no caixa.")

# --- 🏭 PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção Oficina")
    st.session_state.db['producao'] = st.data_editor(st.session_state.db['producao'], num_rows="dynamic", use_container_width=True)
    if st.button("📥 Gerar PDF da Produção"):
        pdf = exportar_pdf("PRODUCAO", st.session_state.db['producao'])
        st.download_button("Baixar Arquivo", pdf, "producao.pdf", "application/pdf")

# --- 📦 ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque de Insumos")
    st.session_state.db['estoque'] = st.data_editor(st.session_state.db['estoque'], num_rows="dynamic", use_container_width=True)
    if st.button("📥 Gerar PDF do Estoque"):
        pdf = exportar_pdf("ESTOQUE", st.session_state.db['estoque'])
        st.download_button("Baixar Arquivo", pdf, "estoque.pdf", "application/pdf")

# --- 💰 FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Controle Financeiro (Entradas e Saídas)")
    st.session_state.db['financeiro'] = st.data_editor(st.session_state.db['financeiro'], num_rows="dynamic", use_container_width=True)
    
    total_e = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    total_s = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Saída']['Valor'].sum()
    st.metric("Saldo em Caixa", f"R$ {total_e - total_s:,.2f}")
    
    if st.button("📥 Gerar Relatório Financeiro (PDF)"):
        pdf = exportar_pdf("FINANCEIRO", st.session_state.db['financeiro'])
        st.download_button("Baixar Arquivo", pdf, "financeiro.pdf", "application/pdf")



 


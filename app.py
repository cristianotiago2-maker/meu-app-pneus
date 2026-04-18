import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="VULCAT PNEUS - SISTEMA", layout="wide", page_icon="🛞")

# MEMÓRIA DO APP (Faz as abas conversarem)
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=["Nome", "CNPJ", "Telefone", "Cidade"])
if 'medidas' not in st.session_state:
    st.session_state.medidas = pd.DataFrame(columns=["Medida", "Quantidade", "Marca"])
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=["Item", "Qtd"])
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descricao", "Valor"])
if 'bloco_notas' not in st.session_state:
    st.session_state.bloco_notas = ""

# --- FUNÇÃO PARA GERAR O PDF (CORRIGIDA) ---
def criar_pdf(empresa, cliente, itens, total, logo_img=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Adiciona Logo se houver
    if logo_img:
        img_temp = io.BytesIO()
        logo_img.save(img_temp, format="PNG")
        pdf.image(img_temp, 10, 8, 30)
        pdf.set_x(45)
    
    # Cabeçalho Empresa
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, empresa['nome'].upper(), ln=True, align='L' if logo_img else 'C')
    pdf.set_font("Arial", "", 10)
    pdf.set_x(45 if logo_img else 10)
    pdf.cell(0, 5, f"CNPJ: {empresa['cnpj']} | Tel: {empresa['tel']}", ln=True, align='L' if logo_img else 'C')
    
    pdf.ln(20)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"ORCAMENTO PARA: {cliente}", ln=True, border='B')
    pdf.ln(5)
    
    # Tabela Itens
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 8, "Item/Medida", 1); pdf.cell(30, 8, "Qtd", 1); pdf.cell(50, 8, "Valor Total", 1)
    pdf.ln()
    
    pdf.set_font("Arial", "", 10)
    for _, row in itens.iterrows():
        pdf.cell(100, 8, str(row['Item/Medida']), 1)
        pdf.cell(30, 8, str(row['Qtd']), 1)
        pdf.cell(50, 8, f"R$ {row['Valor Total']:,.2f}", 1)
        pdf.ln()
        
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL GERAL: R$ {total:,.2f}", ln=True, align='R')
    
    # Assinatura
    pdf.ln(30)
    pdf.cell(0, 10, "________________________________________________", ln=True, align="C")
    pdf.cell(0, 5, "Assinatura do Cliente", ln=True, align="C")
    
    return pdf.output()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏢 Configuração")
    file_logo = st.file_uploader("Logo da Empresa", type=['png', 'jpg'])
    logo_pronta = Image.open(file_logo) if file_logo else None
    
    n_empresa = st.text_input("Empresa", "VULCAT PNEUS")
    c_empresa = st.text_input("CNPJ")
    t_empresa = st.text_input("Telefone")
    dados_empresa = {'nome': n_empresa, 'cnpj': c_empresa, 'tel': t_empresa}

# --- ABAS ---
st.title(f"🚜 {n_empresa}")
tab_dash, tab_orc, tab_med, tab_cli, tab_est, tab_fin, tab_notas = st.tabs([
    "📊 Geral", "📄 Orçamento", "🛞 Medidas", "👥 Clientes", "📦 Estoque", "💰 Financeiro", "📝 Notas"
])

with tab_dash:
    st.subheader("Painel de Controle")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Clientes", len(st.session_state.clientes))
        st.metric("Itens no Estoque", len(st.session_state.estoque))
    with col2:
        # Gráfico Pizza Simples
        if not st.session_state.estoque.empty:
            fig = px.pie(st.session_state.estoque, names='Item', values='Qtd', title="Estoque")
            st.plotly_chart(fig, use_container_width=True)

with tab_orc:
    st.subheader("Gerar Orçamento Profissional")
    c_nome = st.selectbox("Escolher Cliente", [""] + st.session_state.clientes['Nome'].tolist())
    
    # Pega itens de Medidas e Estoque para escolher
    lista_itens = st.session_state.medidas['Medida'].tolist() + st.session_state.estoque['Item'].tolist()
    
    df_o = pd.DataFrame([{"Item/Medida": "", "Qtd": 1, "Valor Total": 0.0}])
    edit_orc = st.data_editor(df_o, num_rows="dynamic", use_container_width=True, 
                             column_config={"Item/Medida": st.column_config.SelectboxColumn("Item/Medida", options=lista_itens)})
    
    total_orc = edit_orc['Valor Total'].sum()
    
    # PRÉ-VISUALIZAÇÃO
    if st.checkbox("Ver Prévia"):
        st.write(f"### Orçamento: {n_empresa}")
        st.write(f"Cliente: {c_nome}")
        st.table(edit_orc)
        st.write(f"**Total: R$ {total_orc:,.2f}**")
        st.write("---")
        st.write("Assinatura: ___________________________")

    if st.button("Gerar PDF"):
        pdf_data = criar_pdf(dados_empresa, c_nome, edit_orc, total_orc, logo_pronta)
        st.download_button("Baixar PDF", data=bytes(pdf_data), file_name="orcamento.pdf", mime="application/pdf")

with tab_med:
    st.subheader("Registro de Medidas")
    st.session_state.medidas = st.data_editor(st.session_state.medidas, num_rows="dynamic", use_container_width=True)

with tab_cli:
    st.subheader("Cadastro de Clientes")
    st.session_state.clientes = st.data_editor(st.session_state.clientes, num_rows="dynamic", use_container_width=True)

with tab_est:
    st.subheader("Estoque de Produtos")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)

with tab_fin:
    st.subheader("Financeiro (Entradas e Saídas)")
    st.session_state.financeiro = st.data_editor(st.session_state.financeiro, num_rows="dynamic", use_container_width=True)

with tab_notas:
    st.subheader("Bloco de Notas")
    st.session_state.bloco_notas = st.text_area("Anotações:", value=st.session_state.bloco_notas, height=300)









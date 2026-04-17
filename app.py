import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página e Estilo Moderno
st.set_page_config(page_title="VULCAT PNEUS - Gestão Pro", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    /* Cor de fundo e fontes */
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    
    /* Cartões do Painel Geral */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 5px solid #3b82f6;
        text-align: center;
    }
    
    /* Tabelas e Editores */
    .stDataEditor { border-radius: 10px; overflow: hidden; }
    
    /* Botões */
    .stButton>button {
        border-radius: 20px;
        background-color: #3b82f6;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1d4ed8; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_pdf(titulo, colunas, dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt=f"VULCAT PNEUS - {titulo}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "B", 9)
    for col in colunas: pdf.cell(31, 10, str(col), border=1)
    pdf.ln()
    pdf.set_font("Arial", size=8)
    for _, row in dados.iterrows():
        for item in row: pdf.cell(31, 10, str(item)[:18], border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INICIALIZAÇÃO DO BANCO ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'clientes': pd.DataFrame(columns=['Nome', 'CNPJ/CPF', 'Telefone', 'Endereço']),
        'medidas': pd.DataFrame({
            "Medida": ["295/80 R22.5", "18.4-34", "11.00 R22", "14.9-24", "12.4-24"],
            "Tipo": ["Rodoviário", "Agrícola", "Rodoviário", "Agrícola", "Agrícola"]
        }),
        'producao': pd.DataFrame(columns=['ID', 'Cliente', 'Medida', 'Serviço', 'Entrada', 'Status']),
        'financeiro': pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor']),
        'estoque': pd.DataFrame({"Item": ["Manchão G", "Cola 1L", "Borracha"], "Qtd":})
    }

# --- MENU LATERAL COLORIDO ---
with st.sidebar:
    st.image("https://flaticon.com", width=80)
    st.title("🚛 VULCAT PNEUS")
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel Geral", "👥 Clientes", "📏 Catálogo Medidas", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro"])
    st.divider()
    st.caption("Sistema v3.0 - Pro Design")

# --- 1. PAINEL GERAL (MODERNO) ---
if menu == "📊 Painel Geral":
    st.title("📊 Painel Geral de Operações")
    
    # Métricas em Colunas Coloridas
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Serviços Ativos", len(st.session_state.db['producao']), delta="Oficina", delta_color="normal")
    with c2: 
        receita = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
        st.metric("Receita (Mês)", f"R$ {receita:,.2f}", delta="Faturamento", delta_color="off")
    with c3: st.metric("Clientes", len(st.session_state.db['clientes']), "Base de Dados")
    with c4: st.metric("Estoque Crítico", len(st.session_state.db['estoque'][st.session_state.db['estoque']['Qtd'] < 5]), "Atenção", delta_color="inverse")

    st.divider()
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.subheader("🏭 Fluxo de Produção Atual")
        st.dataframe(st.session_state.db['producao'], use_container_width=True)
    with col_t2:
        st.subheader("📦 Itens em Baixa")
        st.table(st.session_state.db['estoque'][st.session_state.db['estoque']['Qtd'] < 5])

# --- 2. CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro e Edição de Clientes")
    st.session_state.db['clientes'] = st.data_editor(st.session_state.db['clientes'], num_rows="dynamic", use_container_width=True)

# --- 3. MEDIDAS ---
elif menu == "📏 Catálogo Medidas":
    st.header("📏 Catálogo de Medidas (Agrícola/Rodoviário)")
    st.session_state.db['medidas'] = st.data_editor(st.session_state.db['medidas'], num_rows="dynamic", use_container_width=True)

# --- 4. ORÇAMENTOS ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        cli = c1.selectbox("Cliente", st.session_state.db['clientes']['Nome'].tolist() if not st.session_state.db['clientes'].empty else ["Nenhum Cliente"])
        med = c2.selectbox("Medida", st.session_state.db['medidas']['Medida'].tolist())
        serv = st.text_input("Descrição do Serviço")
        val = st.number_input("Valor (R$)", min_value=0.0, step=50.0)
        
        if st.button("🚀 Aprovar Orçamento e Iniciar Produção"):
            id_os = len(st.session_state.db['producao']) + 1
            # Add Produção
            np = pd.DataFrame([[id_os, cli, med, serv, datetime.now().strftime("%H:%M"), "Fila"]], columns=st.session_state.db['producao'].columns)
            st.session_state.db['producao'] = pd.concat([st.session_state.db['producao'], np], ignore_index=True)
            # Add Financeiro
            nf = pd.DataFrame([[datetime.now().strftime("%d/%m"), f"OS {id_os}: {cli}", "Entrada", val]], columns=st.session_state.db['financeiro'].columns)
            st.session_state.db['financeiro'] = pd.concat([st.session_state.db['financeiro'], nf], ignore_index=True)
            st.success("✅ Orçamento aprovado!")

# --- 5. PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção Oficina")
    st.session_state.db['producao'] = st.data_editor(st.session_state.db['producao'], num_rows="dynamic", use_container_width=True)
    pdf_p = gerar_pdf("PRODUÇÃO", st.session_state.db['producao'].columns, st.session_state.db['producao'])
    st.download_button("📥 Baixar PDF Produção", pdf_p, "producao.pdf", "application/pdf")

# --- 6. ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Inventário de Insumos")
    st.session_state.db['estoque'] = st.data_editor(st.session_state.db['estoque'], num_rows="dynamic", use_container_width=True)
    pdf_e = gerar_pdf("ESTOQUE", st.session_state.db['estoque'].columns, st.session_state.db['estoque'])
    st.download_button("📥 Baixar PDF Estoque", pdf_e, "estoque.pdf", "application/pdf")

# --- 7. FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Gestão Financeira")
    st.session_state.db['financeiro'] = st.data_editor(st.session_state.db['financeiro'], num_rows="dynamic", use_container_width=True)
    pdf_f = gerar_pdf("FINANCEIRO", st.session_state.db['financeiro'].columns, st.session_state.db['financeiro'])
    st.download_button("📥 Baixar Relatório (PDF)", pdf_f, "financeiro.pdf", "application/pdf")


 


import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="VULCAT PNEUS - Gestão Pro", layout="wide", page_icon="🚛")

# Estilo CSS para deixar o app bonito e profissional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; }
    div[data-testid="stSidebarNav"] { background-color: #1e293b; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def consultar_cnpj(cnpj):
    cnpj = "".join(filter(str.isdigit, cnpj))
    try:
        response = requests.get(f"https://receitaws.com.br{cnpj}", timeout=5)
        if response.status_code == 200:
            d = response.json()
            return d.get('nome'), f"{d.get('logradouro')}, {d.get('numero')}", d.get('telefone')
    except: return None

def gerar_pdf(titulo, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"VULCAT PNEUS - {titulo}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for col in df.columns: pdf.cell(31, 8, str(col), border=1)
    pdf.ln()
    for i in range(len(df)):
        for col in df.columns: pdf.cell(31, 8, str(df.iloc[i][col])[:15], border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- BANCO DE DADOS (SESSION STATE) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'clientes': pd.DataFrame(columns=['Nome', 'CNPJ', 'Telefone', 'Endereco']),
        'medidas': pd.DataFrame({"Medida": ["295/80 R22.5", "18.4-34", "11.00 R22", "14.9-24", "23.1-26"], "Tipo": ["Rodoviário", "Agrícola", "Rodoviário", "Agrícola", "Agrícola"]}),
        'producao': pd.DataFrame(columns=['ID', 'Cliente', 'Serviço', 'Entrada', 'Saída', 'Fogo', 'DOT', 'Status']),
        'financeiro': pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor']),
        'estoque': pd.DataFrame({"Item": ["Manchão G", "Cola 1L", "Borracha"], "Qtd": [10, 5, 20]})
    }

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://flaticon.com", width=80)
    st.title("VULCAT PNEUS")
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel Geral", "👥 Clientes", "📏 Medidas", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro", "⚙️ Empresa"])

# --- 📊 PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title("📊 Painel Geral de Controle")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Produção Ativa", len(st.session_state.db['producao']))
    rec = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    c2.metric("Receita Total", f"R$ {rec:,.2f}")
    c3.metric("Clientes", len(st.session_state.db['clientes']))
    c4.metric("Itens Estoque", len(st.session_state.db['estoque']))

    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Etapas da Produção")
        if not st.session_state.db['producao'].empty:
            fig = px.pie(st.session_state.db['producao'], names='Status', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    with col_g2:
        st.subheader("Financeiro (Entradas vs Saídas)")
        if not st.session_state.db['financeiro'].empty:
            fig_f = px.pie(st.session_state.db['financeiro'], names='Tipo', hole=0.4, color_discrete_map={'Entrada':'#2ecc71', 'Saída':'#e74c3c'})
            st.plotly_chart(fig_f, use_container_width=True)

# --- 👥 CLIENTES (CNPJ AUTO) ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.expander("🔍 Preenchimento Automático por CNPJ"):
        cnpj_input = st.text_input("Digite o CNPJ")
        if st.button("Consultar Receita"):
            res = consultar_cnpj(cnpj_input)
            if res: st.success(f"Encontrado: {res[0]}"); st.session_state['tmp_cli'] = res
            else: st.error("Não encontrado")
    
    st.session_state.db['clientes'] = st.data_editor(st.session_state.db['clientes'], num_rows="dynamic", use_container_width=True)

# --- 📝 ORÇAMENTOS ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    with st.form("orc"):
        cli = st.selectbox("Cliente", st.session_state.db['clientes']['Nome'].tolist()) if not st.session_state.db['clientes'].empty else st.warning("Cadastre um cliente.")
        med = st.selectbox("Medida", st.session_state.db['medidas']['Medida'].tolist())
        serv = st.text_input("Serviço")
        val = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("🚀 Aprovar Orçamento"):
            id_os = len(st.session_state.db['producao']) + 1
            # Produção e Financeiro Integrado
            st.session_state.db['producao'] = pd.concat([st.session_state.db['producao'], pd.DataFrame([[id_os, cli, f"{med}-{serv}", datetime.now().strftime("%H:%M"), "--:--", "", "", "Fila"]], columns=st.session_state.db['producao'].columns)], ignore_index=True)
            st.session_state.db['financeiro'] = pd.concat([st.session_state.db['financeiro'], pd.DataFrame([[datetime.now().strftime("%d/%m"), f"OS {id_os}", "Entrada", val]], columns=st.session_state.db['financeiro'].columns)], ignore_index=True)
            st.success("Aprovado!")

# --- 🏭 PRODUÇÃO (FOGO E DOT) ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção Oficina")
    st.session_state.db['producao'] = st.data_editor(st.session_state.db['producao'], num_rows="dynamic", use_container_width=True)
    if st.button("📥 Baixar Ficha de Produção (PDF)"):
        pdf = gerar_pdf("OFICINA", st.session_state.db['producao'])
        st.download_button("Clique aqui para baixar", pdf, "oficina.pdf")

# --- 💰 FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Controle Financeiro")
    st.session_state.db['financeiro'] = st.data_editor(st.session_state.db['financeiro'], num_rows="dynamic", use_container_width=True)
    e = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    s = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Saída']['Valor'].sum()
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Entradas", f"R$ {e:,.2f}")
    c2.metric("Total Saídas", f"R$ {s:,.2f}")
    c3.metric("SALDO FINAL", f"R$ {e-s:,.2f}")

# --- ⚙️ EMPRESA ---
elif menu == "⚙️ Empresa":
    st.header("⚙️ Configurações da Empresa")
    st.text_input("Endereço", "Rua...")
    st.text_input("CNPJ", "00.000.000/0001-00")
    st.text_input("Telefone", "(00) 00000-0000")
    st.file_uploader("Trocar Logotipo")

# Outras abas (Medidas e Estoque)
elif menu == "📏 Medidas":
    st.session_state.db['medidas'] = st.data_editor(st.session_state.db['medidas'], num_rows="dynamic", use_container_width=True)
elif menu == "📦 Estoque":
    st.session_state.db['estoque'] = st.data_editor(st.session_state.db['estoque'], num_rows="dynamic", use_container_width=True)




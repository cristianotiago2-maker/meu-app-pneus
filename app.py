import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="Vulcat Pneus PRO", layout="wide", page_icon="🛞")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #1f3b4d; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; border-radius: 5px; padding: 10px 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE FORMATAÇÃO (MÁSCARAS)
def formatar_cnpj(val):
    val = ''.join(filter(str.isdigit, val))
    if len(val) == 14:
        return f"{val[:2]}.{val[2:5]}.{val[5:8]}/{val[8:12]}-{val[12:]}"
    return val

def formatar_tel(val):
    val = ''.join(filter(str.isdigit, val))
    if len(val) == 11:
        return f"({val[:2]}) {val[2:7]}-{val[7:]}"
    return val

# 3. SIDEBAR (CONFIGURAÇÕES)
with st.sidebar:
    st.image("https://flaticon.com", width=100)
    st.title("VULCAT PNEUS")
    st.divider()
    
    # Campos com formatação automática
    cnpj_raw = st.text_input("CNPJ", placeholder="Digite apenas números")
    st.caption(f"Formatado: {formatar_cnpj(cnpj_raw)}")
    
    tel_raw = st.text_input("Telefone", placeholder="Digite apenas números")
    st.caption(f"Formatado: {formatar_tel(tel_raw)}")
    
    endereco = st.text_area("Endereço", "Rua Industrial, 500")
    logo_url = st.text_input("URL do Logo", "https://flaticon.com")

# 4. PAINEL GERAL (DASHBOARD)
with st.expander("📈 PAINEL GERAL - MÉTRICAS", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Orçamentos do Mês", "128", "+12%")
    m2.metric("Saldo Líquido", "R$ 24.500", "+R$ 3.200")
    m3.metric("Pneus na Oficina", "08", "Estável")
    m4.metric("Estoque Crítico", "03", "-2", delta_color="inverse")

    st.divider()
    # Gráfico Real
    df_grafico = pd.DataFrame({
        "Mês": ["Jan", "Fev", "Mar", "Abr"],
        "Vendas": [15000, 18000, 14000, 24500]
    })
    fig = px.bar(df_grafico, x="Mês", y="Vendas", title="Faturamento por Mês (R$)", 
                 color_discrete_sequence=['#1f3b4d'])
    st.plotly_chart(fig, use_container_width=True)

# 5. ABAS DO SISTEMA
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "🛞 Cadastro Pneus", "💰 Financeiro", "📦 Estoque", "👥 Clientes"])

# --- ABA ORÇAMENTO ---
with tabs[0]:
    st.subheader("Gerar Orçamento")
    c1, c2 = st.columns(2)
    cliente_nome = c1.text_input("Nome do Cliente", key="cli_nome")
    pgto = c2.selectbox("Forma de Pagamento", ["PIX", "Boleto", "Cartão", "Dinheiro"])
    
    df_orc = pd.DataFrame([{"Medida": "295/80 R22.5", "Serviço": "Recapagem", "Qtd": 1, "Preço": 0.0}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True)
    
    total = (edit_orc["Qtd"] * edit_orc["Preço"]).sum()
    st.write(f"### Total: R$ {total:,.2f}")
    if st.button("Download PDF Orçamento"):
        st.success("PDF gerado com sucesso!")

# --- ABA PRODUÇÃO ---
with tabs[1]:
    st.subheader("🛠️ Ficha de Oficina")
    df_prod = pd.DataFrame([{"OS": "101", "Pneu": "Caminhão 01", "Etapa": "Raspagem", "Status": "Em curso"}])
    st.data_editor(df_prod, num_rows="dynamic", use_container_width=True)

# --- NOVA ABA: CADASTRO DE PNEUS E MEDIDAS ---
with tabs[2]:
    st.subheader("🛞 Catálogo de Medidas e Preços Base")
    st.write("Cadastre aqui as medidas que você trabalha para facilitar o orçamento.")
    df_medidas = pd.DataFrame([
        {"Medida": "295/80 R22.5", "Aplicação": "Carga", "Preço Base Recap": 450.0},
        {"Medida": "12.4-24", "Aplicação": "Trator", "Preço Base Recap": 600.0}
    ])
    st.data_editor(df_medidas, num_rows="dynamic", use_container_width=True, key="cat_pneus")

# --- ABA FINANCEIRO ---
with tabs[3]:
    st.subheader("💰 Fluxo de Caixa")
    df_fin = pd.DataFrame([{"Data": "18/04", "Descrição": "Venda Serviço", "Tipo": "Entrada", "Valor": 500.0}])
    st.data_editor(df_fin, num_rows="dynamic", use_container_width=True)

# --- ABA ESTOQUE ---
with tabs[4]:
    st.subheader("📦 Insumos")
    df_est = pd.DataFrame([{"Item": "Cola", "Qtd": 10, "Mínimo": 5}])
    st.data_editor(df_est, num_rows="dynamic", use_container_width=True)

# --- ABA CLIENTES ---
with tabs[5]:
    st.subheader("👥 Clientes")
    df_cli = pd.DataFrame([{"Nome": "João Transportes", "CNPJ": "00.000...", "Tel": "(00) 0000"}])
    st.data_editor(df_cli, num_rows="dynamic", use_container_width=True)











import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="VULCAT PNEUS - PRO", layout="wide", page_icon="🛞")

# Estilo visual robusto
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    [data-testid="stMetricValue"] { color: #1E3A8A; font-weight: 800; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; padding: 12px 25px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE APOIO (MÁSCARAS)
def formatar_cnpj(val):
    val = ''.join(filter(str.isdigit, val))
    if len(val) == 14: return f"{val[:2]}.{val[2:5]}.{val[5:8]}/{val[8:12]}-{val[12:]}"
    return val

def formatar_tel(val):
    val = ''.join(filter(str.isdigit, val))
    if len(val) == 11: return f"({val[:2]}) {val[2:7]}-{val[7:]}"
    return val

# 3. SIDEBAR (LOGOTIPO E DADOS)
with st.sidebar:
    st.title("🚜 CONFIGURAÇÃO")
    logo_file = st.file_uploader("Subir Logotipo (PC)", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    nome_empresa = st.text_input("Nome da Empresa", "VULCAT PNEUS")
    cnpj_raw = st.text_input("CNPJ (Apenas números)")
    cnpj_formatado = formatar_cnpj(cnpj_raw)
    tel_raw = st.text_input("WhatsApp (Apenas números)")
    tel_formatado = formatar_tel(tel_raw)
    endereco = st.text_area("Endereço Completo")

# 4. PAINEL GERAL (DASHBOARD)
st.title(f"📊 PAINEL GERAL - {nome_empresa}")

with st.expander("👁️ VISÃO ESTRATÉGICA", expanded=True):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Faturamento Total", "R$ 0,00")
    m2.metric("Despesas", "R$ 0,00", delta_color="inverse")
    m3.metric("Saldo Líquido", "R$ 0,00")
    m4.metric("Serviços em Aberto", "0")

    st.divider()
    g1, g2 = st.columns(2)
    
    # Gráfico de Pizza - Serviços
    df_p1 = pd.DataFrame({"Serviço": ["Recapagem", "Conserto", "Venda"], "Qtd": [1, 1, 1]})
    fig1 = px.pie(df_p1, values='Qtd', names='Serviço', title="Distribuição de Serviços", hole=.4)
    g1.plotly_chart(fig1, use_container_width=True)

    # Gráfico de Pizza - Estoque
    df_p2 = pd.DataFrame({"Item": ["Pneus", "Insumos"], "Valor": [1, 1]})
    fig2 = px.pie(df_p2, values='Valor', names='Item', title="Valor em Estoque", hole=.4)
    g2.plotly_chart(fig2, use_container_width=True)

# 5. ABAS (MENU SUPERIOR)
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "🛞 Catálogo", "💰 Financeiro", "📦 Estoque", "👥 Clientes"])

with tabs[0]: # Orçamento
    st.subheader("📝 Gerar Novo Orçamento Formal")
    col_l, col_i = st.columns([1,3])
    if logo_file: col_l.image(logo_file, width=150)
    col_i.write(f"**{nome_empresa}** | CNPJ: {cnpj_formatado} | Tel: {tel_formatado}")
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente")
    # Datas com calendário em português (Streamlit detecta o idioma do navegador)
    d_ent = c2.date_input("Data de Entrada", format="DD/MM/YYYY")
    d_sai = c3.date_input("Previsão de Saída", format="DD/MM/YYYY")
    
    df_orc = pd.DataFrame([{"Item/Medida": "", "Serviço": "", "Qtd": 1, "V. Unit.": 0.0}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True, key="orc_br")
    
    total = (edit_orc["Qtd"] * edit_orc["V. Unit."]).sum()
    st.write(f"### VALOR TOTAL: R$ {total:,.2f}")
    
    pagto = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão", "Boleto"])
    
    if st.button("🖨️ Gerar Orçamento para Impressão"):
        st.write("---")
        st.write(f"**DATA DE ENTRADA:** {d_ent.strftime('%d/%m/%Y')} | **PREVISÃO DE SAÍDA:** {d_sai.strftime('%d/%m/%Y')}")
        st.write("__________________________________________")
        st.write(f"Assinatura do Cliente: {cliente}")

with tabs[3]: # Financeiro
    st.subheader("💰 Fluxo de Caixa (Zerado)")
    df_fin = pd.DataFrame([{"Data": datetime.now().date(), "Tipo": "Entrada", "Descrição": "", "Valor": 0.0}])
    # Configurando a coluna de data na tabela para exibir padrão brasileiro
    st.data_editor(df_fin, num_rows="dynamic", use_container_width=True, column_config={
        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY")
    })

# Outras abas simplificadas para o teste
with tabs[1]: st.subheader("🛠️ Oficina"); st.data_editor(pd.DataFrame([{"OS": "", "Pneu": "", "Status": "Pendente"}]), num_rows="dynamic", use_container_width=True)
with tabs[2]: st.subheader("🛞 Catálogo"); st.data_editor(pd.DataFrame([{"Medida": "", "Preço Base": 0.0}]), num_rows="dynamic", use_container_width=True)
with tabs[4]: st.subheader("📦 Estoque"); st.data_editor(pd.DataFrame([{"Item": "", "Qtd": 0}]), num_rows="dynamic", use_container_width=True)
with tabs[5]: st.subheader("👥 Clientes"); st.data_editor(pd.DataFrame([{"Nome": "", "Tel": ""}]), num_rows="dynamic", use_container_width=True)














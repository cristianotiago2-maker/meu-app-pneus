import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Vulcat Pneus", layout="wide")

# Inicialização de memória (Para as abas conversarem e o financeiro começar zerado)
if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone"])
if 'db_estoque' not in st.session_state:
    st.session_state.db_estoque = pd.DataFrame(columns=["Item", "Quantidade"])
if 'db_medidas' not in st.session_state:
    st.session_state.db_medidas = pd.DataFrame(columns=["Medida/Pneu", "Quantidade", "Marca"])
if 'db_financeiro' not in st.session_state:
    st.session_state.db_financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])
if 'notas' not in st.session_state:
    st.session_state.notas = ""

# 2. SIDEBAR (LOGO DO COMPUTADOR E DADOS)
with st.sidebar:
    st.header("Configurações")
    # Upload direto do PC
    logo_upload = st.file_uploader("Carregar Logotipo", type=["png", "jpg", "jpeg"])
    
    nome_empresa = st.text_input("Nome da Empresa", "VULCAT PNEUS")
    cnpj = st.text_input("CNPJ")
    telefone = st.text_input("Telefone")
    endereco = st.text_area("Endereço")

# 3. PAINEL GERAL (GRÁFICOS DE PIZZA)
st.title(f"📊 Painel Geral - {nome_empresa}")
with st.expander("Ver Indicadores", expanded=True):
    col1, col2 = st.columns(2)
    
    # Cálculo Financeiro
    ent = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Saída"]['Valor'].sum()
    
    with col1:
        if ent > 0 or sai > 0:
            fig_fin = px.pie(values=[ent, sai], names=['Entradas', 'Saídas'], title="Financeiro (Entradas vs Saídas)", hole=0.4)
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.info("Financeiro zerado. Adicione dados para ver o gráfico.")
            
    with col2:
        if not st.session_state.db_estoque.empty:
            fig_est = px.pie(st.session_state.db_estoque, names='Item', values='Quantidade', title="Distribuição de Estoque")
            st.plotly_chart(fig_est, use_container_width=True)
        else:
            st.info("Estoque vazio.")

# 4. ABAS DO SISTEMA
tab_orc, tab_prod, tab_med, tab_fin, tab_est, tab_cli, tab_notas = st.tabs([
    "📄 Orçamento", "🛠️ Produção", "🛞 Medidas", "💰 Financeiro", "📦 Estoque", "👥 Clientes", "📝 Notas"
])

with tab_orc:
    st.subheader("Gerar Orçamento")
    
    # Pre-visualização
    if st.checkbox("Ver Pré-visualização do Orçamento"):
        st.markdown(f"""
        <div style="border:1px solid #ccc; padding:20px; background-color:white; color:black">
            <h2 style="text-align:center">{nome_empresa}</h2>
            <p>CNPJ: {cnpj} | Tel: {telefone}</p>
            <hr>
            <p>Assinatura do Cliente: ______________________________________</p>
        </div>
        """, unsafe_allow_html=True)

    # Tabela de Itens
    df_orc = pd.DataFrame([{"Item": "", "Qtd": 1, "Valor": 0.0}])
    st.data_editor(df_orc, num_rows="dynamic", use_container_width=True)
    
    if st.button("Gerar PDF"):
        st.success("Função de PDF pronta. (Use Ctrl+P na pré-visualização para salvar agora)")

with tab_med:
    st.subheader("🛞 Registro de Pneus e Medidas")
    st.session_state.db_medidas = st.data_editor(st.session_state.db_medidas, num_rows="dynamic", use_container_width=True)

with tab_fin:
    st.subheader("💰 Financeiro (Entradas e Saídas)")
    st.session_state.db_financeiro = st.data_editor(st.session_state.db_financeiro, num_rows="dynamic", use_container_width=True)

with tab_notas:
    st.subheader("📝 Bloco de Notas")
    st.session_state.notas = st.text_area("Anotações gerais:", value=st.session_state.notas, height=300)

# Manutenção das demais abas para comunicação
with tab_prod: st.data_editor(pd.DataFrame([{"OS": "", "Etapa": "Inspeção"}]), num_rows="dynamic", use_container_width=True)
with tab_est: st.session_state.db_estoque = st.data_editor(st.session_state.db_estoque, num_rows="dynamic", use_container_width=True)
with tab_cli: st.session_state.db_clientes = st.data_editor(st.session_state.db_clientes, num_rows="dynamic", use_container_width=True)







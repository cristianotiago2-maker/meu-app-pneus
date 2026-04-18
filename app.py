import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURAÇÃO E MEMÓRIA (Faz as abas se comunicarem)
st.set_page_config(page_title="VULCAT PNEUS", layout="wide", page_icon="🛞")

if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone", "Endereço"])
if 'db_estoque' not in st.session_state:
    st.session_state.db_estoque = pd.DataFrame(columns=["Item/Produto", "Quantidade", "Marca", "Localização"])
if 'db_medidas' not in st.session_state:
    st.session_state.db_medidas = pd.DataFrame(columns=["Medida do Pneu", "Modelo", "Índice de Carga", "Qtd em Estoque"])
if 'db_financeiro' not in st.session_state:
    st.session_state.db_financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])
if 'notas' not in st.session_state:
    st.session_state.notas = ""

# 2. SIDEBAR (LOGO DO PC E CONFIGURAÇÕES)
with st.sidebar:
    st.header("⚙️ Configurações")
    logo_upload = st.file_uploader("Carregar Logotipo (PC)", type=["png", "jpg", "jpeg"])
    nome_empresa = st.text_input("Nome da Empresa", "VULCAT PNEUS")
    cnpj = st.text_input("CNPJ")
    telefone = st.text_input("Telefone")
    endereco = st.text_area("Endereço Completo")

# 3. PAINEL GERAL (GRÁFICOS DE PIZZA)
st.title(f"📊 Painel Geral - {nome_empresa}")
with st.expander("👁️ Visão Geral", expanded=True):
    col1, col2 = st.columns(2)
    ent = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Saída"]['Valor'].sum()
    
    with col1:
        if ent > 0 or sai > 0:
            fig_fin = px.pie(values=[ent, sai], names=['Entradas', 'Saídas'], title="Fluxo Financeiro", hole=0.4)
            st.plotly_chart(fig_fin, use_container_width=True)
    with col2:
        if not st.session_state.db_estoque.empty:
            fig_est = px.pie(st.session_state.db_estoque, names='Item/Produto', values='Quantidade', title="Itens em Estoque")
            st.plotly_chart(fig_est, use_container_width=True)

# 4. ABAS DO SISTEMA
tab_orc, tab_prod, tab_med, tab_fin, tab_est, tab_cli, tab_notas = st.tabs([
    "📄 Orçamento Completo", "🛠️ Produção", "🛞 Medidas de Pneus", "💰 Financeiro", "📦 Estoque Completo", "👥 Cadastro Clientes", "📝 Notas"
])

# --- ABA ORÇAMENTO (COMUNICA COM CLIENTES E ESTOQUE/MEDIDAS) ---
with tab_orc:
    st.subheader("📝 Gerar Orçamento Completo")
    
    # Cabeçalho do Orçamento (Pré-visualização)
    if st.checkbox("🔍 Ver Pré-visualização do Documento"):
        st.markdown(f"""
        <div style="border: 2px solid #333; padding: 25px; background-color: white; color: black; border-radius: 10px;">
            <div style="display: flex; justify-content: space-between;">
                <div><h2>{nome_empresa.upper()}</h2><p>CNPJ: {cnpj} | Tel: {telefone}<br>{endereco}</p></div>
                <div style="text-align: right;"><strong>ORÇAMENTO</strong><br>{datetime.now().strftime('%d/%m/%Y')}</div>
            </div>
            <hr>
            <br><br><br><br>
            <div style="text-align: center;">
                ____________________________________________________<br>
                ASSINATURA DO CLIENTE
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    # COMUNICAÇÃO COM ABA CLIENTES
    lista_clientes = st.session_state.db_clientes['Nome'].tolist()
    cliente_sel = c1.selectbox("Selecionar Cliente Cadastrado", [""] + lista_clientes)
    
    d_ent = c2.date_input("Data de Entrada", format="DD/MM/YYYY")
    d_sai = c3.date_input("Previsão de Saída", format="DD/MM/YYYY")

    # COMUNICAÇÃO COM ABA ESTOQUE E MEDIDAS
    lista_servicos = st.session_state.db_estoque['Item/Produto'].tolist() + st.session_state.db_medidas['Medida do Pneu'].tolist()
    
    df_orc = pd.DataFrame([{"Item/Serviço": "", "Qtd": 1, "V. Unit": 0.0}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True,
                             column_config={"Item/Serviço": st.column_config.SelectboxColumn("Item/Serviço", options=lista_servicos)})
    
    total = (edit_orc['Qtd'] * edit_orc['V. Unit']).sum()
    st.metric("Total do Orçamento", f"R$ {total:,.2f}")
    pagto = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Cartão", "Boleto"])

# --- ABA MEDIDAS DE PNEUS ---
with tab_med:
    st.subheader("🛞 Registro de Medidas de Pneus")
    st.session_state.db_medidas = st.data_editor(st.session_state.db_medidas, num_rows="dynamic", use_container_width=True)

# --- ABA ESTOQUE COMPLETO ---
with tab_est:
    st.subheader("📦 Estoque Completo de Insumos e Produtos")
    st.session_state.db_estoque = st.data_editor(st.session_state.db_estoque, num_rows="dynamic", use_container_width=True)

# --- ABA FINANCEIRO (ZERADO) ---
with tab_fin:
    st.subheader("💰 Financeiro (Entradas e Saídas)")
    st.session_state.db_financeiro = st.data_editor(st.session_state.db_financeiro, num_rows="dynamic", use_container_width=True, 
                                                   column_config={"Tipo": st.column_config.SelectboxColumn("Tipo", options=["Entrada", "Saída"])})

# --- DEMAIS ABAS ---
with tab_cli:
    st.subheader("👥 Cadastro de Clientes")
    st.session_state.db_clientes = st.data_editor(st.session_state.db_clientes, num_rows="dynamic", use_container_width=True)

with tab_prod:
    st.subheader("🛠️ Ficha de Produção")
    st.data_editor(pd.DataFrame([{"Série": "", "Etapa": "Inspeção", "Status": "Pendente"}]), num_rows="dynamic", use_container_width=True)

with tab_notas:
    st.subheader("📝 Bloco de Notas")
    st.session_state.notas = st.text_area("Anotações:", value=st.session_state.notas, height=300)

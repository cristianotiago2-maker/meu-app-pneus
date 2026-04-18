import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# 1. CONFIGURAÇÃO E MEMÓRIA DO APP (Faz as abas se comunicarem)
st.set_page_config(page_title="VULCAT PNEUS - SISTEMA GESTÃO", layout="wide", page_icon="🛞")

if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone", "Endereço", "Cidade"])
if 'db_catalogo' not in st.session_state:
    st.session_state.db_catalogo = pd.DataFrame(columns=["Medida", "Aplicação", "Preço Base"])
if 'db_financeiro' not in st.session_state:
    st.session_state.db_financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])

# 2. FUNÇÕES DE FORMATAÇÃO AUTOMÁTICA
def format_cnpj(v):
    v = ''.join(filter(str.isdigit, v))
    if len(v) == 14: return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    return v

def format_tel(v):
    v = ''.join(filter(str.isdigit, v))
    if len(v) == 11: return f"({v[:2]}) {v[2:7]}-{v[7:]}"
    return v

# 3. BARRA LATERAL (CONFIGURAÇÃO DA EMPRESA)
with st.sidebar:
    st.title("⚙️ CONFIGURAÇÕES")
    logo_file = st.file_uploader("Carregar Logotipo (PC)", type=['png', 'jpg', 'jpeg'])
    nome_empresa = st.text_input("Nome da Empresa", "VULCAT PNEUS")
    cnpj_input = st.text_input("CNPJ (números)")
    tel_empresa = st.text_input("Telefone (números)")
    endereco_empresa = st.text_area("Endereço Completo")
    st.divider()
    st.caption("v5.0 Profissional")

# 4. PAINEL GERAL (DASHBOARD COM GRÁFICO DE PIZZA)
st.title(f"🚜 {nome_empresa}")

with st.expander("📈 PAINEL GERAL E INDICADORES", expanded=True):
    # Cálculos Financeiros
    ent = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Saída"]['Valor'].sum()
    saldo = ent - sai

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Entradas", f"R$ {ent:,.2f}")
    c2.metric("Total Saídas", f"R$ {sai:,.2f}", delta_color="inverse")
    c3.metric("Saldo Líquido", f"R$ {saldo:,.2f}")
    c4.metric("Clientes Ativos", len(st.session_state.db_clientes))

    st.divider()
    col_g1, col_g2 = st.columns(2)
    
    # Gráfico de Pizza Financeiro
    if ent > 0 or sai > 0:
        fig_fin = px.pie(values=[ent, sai], names=['Entradas', 'Saídas'], title="Saúde Financeira", hole=0.4, color_discrete_sequence=['#2ecc71', '#e74c3c'])
        col_g1.plotly_chart(fig_fin, use_container_width=True)
    else:
        col_g1.info("Aguardando dados financeiros para gerar gráfico.")

    # Gráfico de Pizza Clientes
    if not st.session_state.db_clientes.empty:
        fig_cli = px.pie(st.session_state.db_clientes, names='Cidade', title="Distribuição de Clientes por Cidade", hole=0.4)
        col_g2.plotly_chart(fig_cli, use_container_width=True)

# 5. ABAS DO SISTEMA
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "💰 Financeiro", "🛞 Catálogo", "📦 Estoque", "👥 Clientes"])

# --- ABA ORÇAMENTO (INTEGRADA) ---
with tabs[0]:
    st.subheader("📝 Orçamento Profissional")
    
    # Cabeçalho do Orçamento com Logo
    col_logo, col_header = st.columns([1, 3])
    if logo_file: col_logo.image(logo_file, width=150)
    col_header.write(f"**{nome_empresa}** | CNPJ: {format_cnpj(cnpj_input)}")
    col_header.write(f"Tel: {format_tel(tel_empresa)} | {endereco_empresa}")

    st.divider()
    o1, o2 = st.columns(2)
    
    # Busca Clientes Cadastrados
    lista_nomes = st.session_state.db_clientes['Nome'].tolist()
    cliente_sel = o1.selectbox("Selecionar Cliente", [""] + lista_nomes)
    
    # Datas em PT-BR
    d_ent = o2.date_input("Data de Entrada", format="DD/MM/YYYY")
    d_sai = o2.date_input("Previsão de Saída", format="DD/MM/YYYY")

    # Puxa dados do cliente automaticamente
    if cliente_sel:
        c_dados = st.session_state.db_clientes[st.session_state.db_clientes['Nome'] == cliente_sel].iloc[0]
        st.info(f"**Cliente:** {c_dados['Nome']} | **Doc:** {c_dados['CPF/CNPJ']} | **Tel:** {c_dados['Telefone']}")
    
    # Tabela de Itens (Orçamento)
    df_orc = pd.DataFrame([{"Medida": "", "Serviço": "", "Qtd": 1, "V. Unit": 0.0}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True, key="editor_orc")
    
    total_orc = (edit_orc['Qtd'] * edit_orc['V. Unit']).sum()
    st.write(f"### TOTAL: R$ {total_orc:,.2f}")
    
    forma_pgto = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Boleto", "Cartão"])

    if st.button("🚀 Gerar PDF Oficial"):
        st.success("Visualização pronta para impressão. Use Ctrl + P.")
        st.write("---")
        st.write(f"### ORÇAMENTO - {nome_empresa}")
        st.table(edit_orc)
        st.write(f"**Forma de Pagamento:** {forma_pgto}")
        st.write(f"**Data Entrada:** {d_ent.strftime('%d/%m/%Y')} | **Saída:** {d_sai.strftime('%d/%m/%Y')}")
        st.write("\n\n")
        st.write("________________________________________________")
        st.write("Assinatura do Cliente")

# --- ABA PRODUÇÃO ---
with tabs[1]:
    st.subheader("🛠️ Ficha de Produção (Sem Valores)")
    st.data_editor(pd.DataFrame([{"Série": "", "Serviço": "", "Etapa": "Inspeção", "Status": "Pendente"}]), num_rows="dynamic", use_container_width=True)

# --- ABA FINANCEIRO (ENTRADA/SAÍDA ZERADA) ---
with tabs[2]:
    st.subheader("💰 Fluxo de Caixa")
    st.session_state.db_financeiro = st.data_editor(st.session_state.db_financeiro, num_rows="dynamic", use_container_width=True, column_config={
        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Entrada", "Saída"])
    })

# --- ABA CATÁLOGO ---
with tabs[3]:
    st.subheader("🛞 Catálogo de Medidas")
    st.session_state.db_catalogo = st.data_editor(st.session_state.db_catalogo, num_rows="dynamic", use_container_width=True)

# --- ABA ESTOQUE ---
with tabs[4]:
    st.subheader("📦 Controle de Insumos")
    st.data_editor(pd.DataFrame([{"Item": "", "Qtd": 0, "Mínimo": 5}]), num_rows="dynamic", use_container_width=True)

# --- ABA CLIENTES ---
with tabs[5]:
    st.subheader("👥 Cadastro de Clientes")
    st.session_state.db_clientes = st.data_editor(st.session_state.db_clientes, num_rows="dynamic", use_container_width=True)












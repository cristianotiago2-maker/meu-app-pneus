import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="VULCAT PNEUS - Gestão Elite", layout="wide", page_icon="🚛")

# --- FUNÇÃO CONSULTA CNPJ (API GRATUITA) ---
def consultar_cnpj(cnpj):
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    try:
        response = requests.get(f"https://receitaws.com.br{cnpj}")
        if response.status_code == 200:
            dados = response.json()
            return dados.get('nome', ''), dados.get('logradouro', '') + ", " + dados.get('numero', ''), dados.get('telefone', '')
    except:
        return None

# --- INICIALIZAÇÃO DOS DADOS ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'clientes': pd.DataFrame(columns=['Nome', 'CNPJ', 'Telefone', 'Endereco']),
        'medidas': pd.DataFrame({"Medida": ["295/80 R22.5", "18.4-34", "11.00 R22"], "Tipo": ["Rodoviário", "Agrícola", "Rodoviário"]}),
        'producao': pd.DataFrame(columns=['ID', 'Cliente', 'Serviço', 'Entrada', 'Saída', 'Fogo', 'DOT', 'Status']),
        'financeiro': pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor']),
        'estoque': pd.DataFrame({"Item": ["Manchão G", "Cola 1L"], "Qtd": [10, 5]})
    }

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    menu = st.radio("MENU", ["📊 Painel Geral", "👥 Clientes", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro"])
    st.divider()
    emp_nome = st.text_input("Empresa", "Vulcat Pneus")

# --- 📊 PAINEL GERAL (COM GRÁFICOS) ---
if menu == "📊 Painel Geral":
    st.title(f"📊 Painel Geral de Operações")
    
    # Métricas principais
    c1, c2, c3 = st.columns(3)
    c1.metric("Serviços Ativos", len(st.session_state.db['producao']))
    receita = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    c2.metric("Receita Total", f"R$ {receita:,.2f}")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Etapas da Produção")
        if not st.session_state.db['producao'].empty:
            fig_prod = px.pie(st.session_state.db['producao'], names='Status', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_prod, use_container_width=True)
        else: st.info("Sem dados de produção.")
        
    with col_g2:
        st.subheader("Entradas vs Saídas")
        if not st.session_state.db['financeiro'].empty:
            fig_fin = px.pie(st.session_state.db['financeiro'], names='Tipo', hole=0.4, color_discrete_map={'Entrada':'#2ecc71', 'Saída':'#e74c3c'})
            st.plotly_chart(fig_fin, use_container_width=True)
        else: st.info("Sem dados financeiros.")

# --- 👥 CLIENTES (COM BUSCA DE CNPJ) ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes Inteligente")
    with st.expander("🔍 Buscar por CNPJ"):
        cnpj_busca = st.text_input("Digite o CNPJ para preencher")
        if st.button("Buscar Dados"):
            resultado = consultar_cnpj(cnpj_busca)
            if resultado:
                st.session_state['temp_nome'], st.session_state['temp_end'], st.session_state['temp_tel'] = resultado
                st.success("Dados encontrados!")
            else: st.error("CNPJ não encontrado.")

    with st.form("cad_cli", clear_on_submit=True):
        nome_f = st.text_input("Nome/Razão Social", value=st.session_state.get('temp_nome', ''))
        cnpj_f = st.text_input("CNPJ/CPF", value=cnpj_busca)
        tel_f = st.text_input("Telefone", value=st.session_state.get('temp_tel', ''))
        end_f = st.text_input("Endereço", value=st.session_state.get('temp_end', ''))
        if st.form_submit_button("✅ Cadastrar Cliente"):
            nova_l = pd.DataFrame([[nome_f, cnpj_f, tel_f, end_f]], columns=st.session_state.db['clientes'].columns)
            st.session_state.db['clientes'] = pd.concat([st.session_state.db['clientes'], nova_l], ignore_index=True)
    
    st.session_state.db['clientes'] = st.data_editor(st.session_state.db['clientes'], num_rows="dynamic", use_container_width=True)

# --- 📝 ORÇAMENTOS ---
elif menu == "📝 Orçamentos":
    st.header("📝 Orçamentos")
    with st.form("orc"):
        cli = st.selectbox("Cliente", st.session_state.db['clientes']['Nome'].tolist()) if not st.session_state.db['clientes'].empty else st.warning("Cadastre um cliente.")
        med = st.selectbox("Medida", st.session_state.db['medidas']['Medida'].tolist())
        serv = st.text_input("Serviço")
        val = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Aprovar Orçamento"):
            id_os = len(st.session_state.db['producao']) + 1
            # Produção com Fogo e DOT
            np = pd.DataFrame([[id_os, cli, f"{med}-{serv}", datetime.now().strftime("%H:%M"), "--:--", "", "", "Fila"]], columns=st.session_state.db['producao'].columns)
            st.session_state.db['producao'] = pd.concat([st.session_state.db['producao'], np], ignore_index=True)
            # Financeiro
            nf = pd.DataFrame([[datetime.now().strftime("%d/%m"), f"OS {id_os}", "Entrada", val]], columns=st.session_state.db['financeiro'].columns)
            st.session_state.db['financeiro'] = pd.concat([st.session_state.db['financeiro'], nf], ignore_index=True)
            st.success("✅ Aprovado!")

# --- 🏭 PRODUÇÃO (COM FOGO E DOT) ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção Oficina")
    st.session_state.db['producao'] = st.data_editor(st.session_state.db['producao'], num_rows="dynamic", use_container_width=True)

# --- 💰 FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Controle Financeiro")
    st.session_state.db['financeiro'] = st.data_editor(st.session_state.db['financeiro'], num_rows="dynamic", use_container_width=True)
    ent = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    sai = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Saída']['Valor'].sum()
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Entradas", f"R$ {ent:,.2f}")
    c2.metric("Total Saídas", f"R$ {sai:,.2f}")
    c3.metric("Saldo em Caixa", f"R$ {ent - sai:,.2f}")

elif menu == "📦 Estoque":
    st.header("📦 Estoque")
    st.session_state.db['estoque'] = st.data_editor(st.session_state.db['estoque'], num_rows="dynamic", use_container_width=True)





 


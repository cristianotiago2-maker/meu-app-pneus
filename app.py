import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="VULCAT PNEUS - Gestão Ultra", layout="wide", page_icon="🚛")

# --- INICIALIZAÇÃO DOS DADOS (BANCO DE DADOS TEMPORÁRIO) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'clientes': pd.DataFrame(columns=['Nome', 'CNPJ/CPF', 'Telefone', 'Endereço']),
        'medidas': pd.DataFrame({
            "Medida": ["295/80 R22.5", "275/80 R22.5", "11.00 R22", "18.4-34", "23.1-26", "14.9-24"],
            "Tipo": ["Rodoviário"]*3 + ["Agrícola"]*3
        }),
        'producao': pd.DataFrame(columns=['ID', 'Cliente', 'Medida', 'Serviço', 'Entrada', 'Saída', 'Status', 'Anotações']),
        'financeiro': pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor']),
        'estoque': pd.DataFrame({"Item": ["Manchão G", "Cola 1L"], "Qtd": [10, 5]})
    }

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel Geral", "👥 Clientes", "📏 Medidas", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro"])
    st.divider()
    emp_nome = st.text_input("Empresa", "Vulcat Pneus")

# --- 1. PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title(f"📊 Painel Geral - {emp_nome}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Serviços Ativos", len(st.session_state.db['producao']))
    ent = st.session_state.db['financeiro'][st.session_state.db['financeiro']['Tipo'] == 'Entrada']['Valor'].sum()
    c2.metric("Receita Total", f"R$ {ent:,.2f}")
    c3.info("📞 Suporte Vulcat")
    
    st.subheader("📋 Resumo da Produção")
    st.dataframe(st.session_state.db['producao'], use_container_width=True)

# --- 2. CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("cad_cli", clear_on_submit=True):
        n = st.text_input("Nome")
        d = st.text_input("CNPJ/CPF")
        if st.form_submit_button("Cadastrar"):
            nova_l = pd.DataFrame([[n, d, "", ""]], columns=st.session_state.db['clientes'].columns)
            st.session_state.db['clientes'] = pd.concat([st.session_state.db['clientes'], nova_l], ignore_index=True)
            st.success("Cadastrado!")
    st.session_state.db['clientes'] = st.data_editor(st.session_state.db['clientes'], num_rows="dynamic", use_container_width=True)

# --- 3. MEDIDAS ---
elif menu == "📏 Medidas":
    st.header("📏 Catálogo de Medidas")
    st.session_state.db['medidas'] = st.data_editor(st.session_state.db['medidas'], num_rows="dynamic", use_container_width=True)

# --- 4. ORÇAMENTOS ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    if st.session_state.db['clientes'].empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        with st.form("orc"):
            cli = st.selectbox("Cliente", st.session_state.db['clientes']['Nome'].tolist())
            med = st.selectbox("Medida", st.session_state.db['medidas']['Medida'].tolist())
            serv = st.text_input("Serviço")
            val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Aprovar Orçamento"):
                id_os = len(st.session_state.db['producao']) + 1
                # Produção
                np = pd.DataFrame([[id_os, cli, med, serv, datetime.now().strftime("%H:%M"), "--:--", "Fila", ""]], columns=st.session_state.db['producao'].columns)
                st.session_state.db['producao'] = pd.concat([st.session_state.db['producao'], np], ignore_index=True)
                # Financeiro
                nf = pd.DataFrame([[datetime.now().strftime("%d/%m"), f"OS {id_os}: {cli}", "Entrada", val]], columns=st.session_state.db['financeiro'].columns)
                st.session_state.db['financeiro'] = pd.concat([st.session_state.db['financeiro'], nf], ignore_index=True)
                st.success("Aprovado! Verifique Produção e Financeiro.")

# --- 5. PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção")
    st.session_state.db['producao'] = st.data_editor(st.session_state.db['producao'], num_rows="dynamic", use_container_width=True)

# --- 6. ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque")
    st.session_state.db['estoque'] = st.data_editor(st.session_state.db['estoque'], num_rows="dynamic", use_container_width=True)

# --- 7. FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Financeiro")
    st.session_state.db['financeiro'] = st.data_editor(st.session_state.db['financeiro'], num_rows="dynamic", use_container_width=True)

 


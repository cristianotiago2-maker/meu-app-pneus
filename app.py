
Tiago Cristiano da Silva <cristianotiago2@gmail.com>
20:10 (há 0 minuto)
para mim

import streamlit as st
import pandas as pd
from datetime import datetime

# Configurações de Layout
st.set_page_config(page_title="VULCAT PNEUS - Gestão Integrada", layout="wide", page_icon="🚛")

# --- INICIALIZAÇÃO DO BANCO DE DADOS NA MEMÓRIA ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['Nome', 'CNPJ/CPF', 'Telefone', 'Endereço'])
if 'orcamentos' not in st.session_state:
    st.session_state.orcamentos = pd.DataFrame(columns=['ID', 'Cliente', 'Serviço', 'Valor', 'Status'])
if 'producao' not in st.session_state:
    st.session_state.producao = pd.DataFrame(columns=['ID', 'Cliente', 'Pneu', 'Entrada', 'Saída', 'Anotações', 'Status'])
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor'])
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame({"Item": ["Pneu 295/80", "Manchão", "Cola"], "Qtd": [10, 50, 5]})

# --- BARRA LATERAL (MENU E DADOS DA EMPRESA) ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    st.divider()
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel Geral", "👥 Clientes", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro", "⚙️ Config. Empresa"])
    
    st.divider()
    st.info("Configurações da Empresa")
    empresa_nome = st.text_input("Nome da Empresa", "Vulcat Pneus")
    empresa_cnpj = st.text_input("CNPJ Empresa", "00.000.000/0001-00")

# --- ⚙️ CONFIG. EMPRESA ---
if menu == "⚙️ Config. Empresa":
    st.header("⚙️ Cadastro da Empresa")
    st.text_input("Endereço Completo", key="end_emp")
    st.text_input("Telefone de Contato", key="tel_emp")
    st.file_uploader("Upload do Logotipo")

# --- 👥 CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("cad_cliente"):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome/Razão Social")
        d = c2.text_input("CNPJ/CPF")
        t = c1.text_input("Telefone")
        e = c2.text_input("Endereço")
        if st.form_submit_button("Cadastrar Cliente"):
            nova_l = pd.DataFrame([[n, d, t, e]], columns=st.session_state.clientes.columns)
            st.session_state.clientes = pd.concat([st.session_state.clientes, nova_l], ignore_index=True)
    
    st.subheader("Clientes Cadastrados")
    st.session_state.clientes = st.data_editor(st.session_state.clientes, num_rows="dynamic", use_container_width=True)

# --- 📝 ORÇAMENTOS (LIGADO À PRODUÇÃO E CAIXA) ---
elif menu == "📝 Orçamentos":
    st.header("📝 Orçamentos")
    with st.form("gera_orc"):
        cliente_sel = st.selectbox("Selecionar Cliente", st.session_state.clientes['Nome'].unique() if not st.session_state.clientes.empty else ["Cadastre um cliente primeiro"])
        serv = st.text_input("Descrição do Serviço/Pneu")
        v = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Gerar e Aprovar Orçamento"):
            id_gera = len(st.session_state.orcamentos) + 1
            # 1. Salva Orçamento
            st.session_state.orcamentos = pd.concat([st.session_state.orcamentos, pd.DataFrame([[id_gera, cliente_sel, serv, v, 'Aprovado']], columns=st.session_state.orcamentos.columns)], ignore_index=True)
            # 2. Manda para Produção
            st.session_state.producao = pd.concat([st.session_state.producao, pd.DataFrame([[id_gera, cliente_sel, serv, datetime.now().strftime("%H:%M"), "--:--", "", "Na Fila"]], columns=st.session_state.producao.columns)], ignore_index=True)
            # 3. Lança no Financeiro
            st.session_state.financeiro = pd.concat([st.session_state.financeiro, pd.DataFrame([[datetime.now().strftime("%d/%m"), f"Venda: {cliente_sel}", "Entrada", v]], columns=st.session_state.financeiro.columns)], ignore_index=True)
            st.success("Orçamento Aprovado! Dados enviados para Produção e Financeiro.")

# --- 🏭 PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção (Editável)")
    st.session_state.producao = st.data_editor(st.session_state.producao, num_rows="dynamic", use_container_width=True)
    st.caption("Dica: Edite os horários e anotações diretamente na tabela acima.")

# --- 📦 ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Controle de Estoque")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)

# --- 💰 FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Fluxo de Caixa")
    st.session_state.financeiro = st.data_editor(st.session_state.financeiro, num_rows="dynamic", use_container_width=True)
    receita = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Entrada']['Valor'].sum()
    despesa = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Saída']['Valor'].sum()
    st.metric("Saldo em Caixa", f"R$ {receita - despesa:,.2f}", delta=f"Rec: {receita}")

# --- 📊 PAINEL GERAL ---
else:
    st.title(f"📊 Painel Geral - {empresa_nome}")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("🏭 Produção Ativa")
        st.write(st.session_state.producao[st.session_state.producao['Status'] != 'Finalizado'])
    with c2:
        st.subheader("📦 Alerta Estoque")
        st.write(st.session_state.estoque[st.session_state.estoque['Qtd'] < 5])
    with c3:
        st.subheader("💰 Resumo Caixa")
        rec = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Entrada']['Valor'].sum()
        st.metric("Total Entradas", f"R$ {rec:,.2f}")




import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="VULCAT PNEUS - Gestão Pro", layout="wide", page_icon="🚛")

# --- INICIALIZAÇÃO DO BANCO DE DADOS (MEMÓRIA) ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['Nome', 'CNPJ/CPF', 'Telefone', 'Endereço'])
if 'producao' not in st.session_state:
    st.session_state.producao = pd.DataFrame(columns=['ID', 'Cliente', 'Serviço', 'Entrada', 'Saída', 'Status', 'Anotações'])
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor'])
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame({"Item": ["Pneu 295/80", "Manchão", "Cola"], "Qtd": [10, 50, 5]})

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel Geral", "👥 Clientes", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro", "⚙️ Empresa"])
    st.write("---")
    # Configurações Rápidas da Empresa
    emp_nome = st.text_input("Sua Empresa", "Vulcat Pneus")
    emp_tel = st.text_input("Telefone", "(00) 00000-0000")

# --- ⚙️ CONFIGURAÇÃO DA EMPRESA ---
if menu == "⚙️ Empresa":
    st.header("⚙️ Configurações da Empresa")
    st.text_input("CNPJ", "00.000.000/0001-00")
    st.text_input("Endereço Completo", "Rua Exemplo, 123")
    st.file_uploader("Logotipo da Empresa")

# --- 👥 CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("cad_cliente", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome / Razão Social")
        d = c2.text_input("CNPJ / CPF")
        t = c1.text_input("Telefone")
        e = c2.text_input("Endereço")
        if st.form_submit_button("✅ Cadastrar"):
            nova_l = pd.DataFrame([[n, d, t, e]], columns=st.session_state.clientes.columns)
            st.session_state.clientes = pd.concat([st.session_state.clientes, nova_l], ignore_index=True)
            st.success("Cliente Cadastrado!")
    
    st.subheader("Lista de Clientes (Editável)")
    st.session_state.clientes = st.data_editor(st.session_state.clientes, num_rows="dynamic", use_container_width=True)

# --- 📝 ORÇAMENTOS (O CORAÇÃO DO APP) ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    if st.session_state.clientes.empty:
        st.warning("⚠️ Cadastre um cliente primeiro na aba 'Clientes'.")
    else:
        with st.form("form_orc"):
            cliente_sel = st.selectbox("Selecione o Cliente", st.session_state.clientes['Nome'].tolist())
            servico = st.text_input("Descrição do Pneu / Serviço (Ex: Vulcanização 295/80)")
            valor = st.number_input("Valor do Serviço R$", min_value=0.0)
            
            if st.form_submit_button("🚀 Aprovar e Iniciar Produção"):
                # 1. Manda para Produção
                id_os = len(st.session_state.producao) + 1
                hora_in = datetime.now().strftime("%H:%M")
                nova_p = pd.DataFrame([[id_os, cliente_sel, servico, hora_in, "--:--", "Em Produção", ""]], columns=st.session_state.producao.columns)
                st.session_state.producao = pd.concat([st.session_state.producao, nova_p], ignore_index=True)
                
                # 2. Manda para o Financeiro (Entrada)
                data_hoje = datetime.now().strftime("%d/%m")
                nova_f = pd.DataFrame([[data_hoje, f"Serviço: {servico} ({cliente_sel})", "Entrada", valor]], columns=st.session_state.financeiro.columns)
                st.session_state.financeiro = pd.concat([st.session_state.financeiro, nova_f], ignore_index=True)
                
                st.success(f"Orçamento aprovado! Serviço {id_os} já está na oficina.")

# --- 🏭 PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção (Oficina)")
    st.write("Edite os horários de saída e anotações diretamente na tabela:")
    st.session_state.producao = st.data_editor(st.session_state.producao, num_rows="dynamic", use_container_width=True)

# --- 📦 ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque de Pneus e Insumos")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)

# --- 💰 FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Controle de Caixa")
    st.session_state.financeiro = st.data_editor(st.session_state.financeiro, num_rows="dynamic", use_container_width=True)
    
    total_ent = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Entrada']['Valor'].sum()
    total_sai = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Saída']['Valor'].sum()
    st.metric("Saldo Geral", f"R$ {total_ent - total_sai:,.2f}", delta=f"Receita: {total_ent}")

# --- 📊 PAINEL GERAL ---
else:
    st.title(f"📊 Painel Geral - {emp_nome}")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("⚙️ Oficina Ativa")
        st.dataframe(st.session_state.producao[st.session_state.producao['Status'] != 'Finalizado'], use_container_width=True)
    
    with c2:
        st.subheader("📦 Alerta de Estoque")
        st.dataframe(st.session_state.estoque[st.session_state.estoque['Qtd'] < 5], use_container_width=True)
        
    with c3:
        st.subheader("💰 Resumo do Dia")
        rec = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Entrada']['Valor'].sum()
        st.metric("Entradas Hoje", f"R$ {rec:,.2f}")
        st.write(f"📞 Contato: {emp_tel}")


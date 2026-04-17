import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="VULCAT PNEUS - Gestão Ultra", layout="wide", page_icon="🚛")

# --- INICIALIZAÇÃO DOS BANCO DE DADOS ---
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['Nome', 'CNPJ/CPF', 'Telefone', 'Endereço'])

if 'medidas' not in st.session_state:
    # Cadastro inicial de medidas (Rodoviário e Agrícola)
    medidas_ini = [
        # Rodoviário
        "295/80 R22.5", "275/80 R22.5", "11.00 R22", "10.00 R20", "12.00 R24", "215/75 R17.5",
        # Agrícola / Trator
        "18.4-34", "23.1-26", "14.9-24", "12.4-24", "18.4-30", "20.8-38", "420/85 R24", "520/85 R38", "600/50 R22.5", "10.5/80-18"
    ]
    st.session_state.medidas = pd.DataFrame({"Medida": medidas_ini, "Tipo": ["Rodoviário"]*6 + ["Agrícola"]*10})

if 'producao' not in st.session_state:
    st.session_state.producao = pd.DataFrame(columns=['ID', 'Cliente', 'Medida', 'Serviço', 'Entrada', 'Saída', 'Status', 'Anotações'])

if 'financeiro' not in st.session_state:
    st.session_state.financeiro = pd.DataFrame(columns=['Data', 'Descrição', 'Tipo', 'Valor'])

if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame({"Item": ["Manchão G", "Manchão P", "Cola 1L", "Borracha Ligação"], "Qtd":})

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🚛 VULCAT PNEUS")
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel Geral", "👥 Clientes", "📏 Catálogo de Medidas", "📝 Orçamentos", "🏭 Produção", "📦 Estoque", "💰 Financeiro", "⚙️ Empresa"])
    st.write("---")
    emp_nome = st.text_input("Sua Empresa", "Vulcat Pneus")

# --- 📏 CATÁLOGO DE MEDIDAS (EDITÁVEL) ---
if menu == "📏 Catálogo de Medidas":
    st.header("📏 Catálogo de Medidas (Rodoviário e Agrícola)")
    st.write("Adicione ou edite medidas que aparecerão nos orçamentos:")
    st.session_state.medidas = st.data_editor(st.session_state.medidas, num_rows="dynamic", use_container_width=True)

# --- 👥 CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("cad_cliente", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome / Razão Social")
        d = c2.text_input("CNPJ / CPF")
        t = c1.text_input("Telefone")
        e = c2.text_input("Endereço")
        if st.form_submit_button("✅ Cadastrar Cliente"):
            nova_l = pd.DataFrame([[n, d, t, e]], columns=st.session_state.clientes.columns)
            st.session_state.clientes = pd.concat([st.session_state.clientes, nova_l], ignore_index=True)
            st.success("Cliente Cadastrado!")
    st.session_state.clientes = st.data_editor(st.session_state.clientes, num_rows="dynamic", use_container_width=True)

# --- 📝 ORÇAMENTOS (INTEGRADO) ---
elif menu == "📝 Orçamentos":
    st.header("📝 Novo Orçamento")
    if st.session_state.clientes.empty:
        st.warning("⚠️ Cadastre um cliente primeiro.")
    else:
        with st.form("form_orc"):
            col1, col2 = st.columns(2)
            cli = col1.selectbox("Selecione o Cliente", st.session_state.clientes['Nome'].tolist())
            med = col2.selectbox("Selecione a Medida", st.session_state.medidas['Medida'].tolist())
            serv = st.text_input("Descrição do Serviço (Ex: Vulcanização Lateral)")
            val = st.number_input("Valor R$", min_value=0.0)
            
            if st.form_submit_button("🚀 Aprovar e Iniciar Produção"):
                id_os = len(st.session_state.producao) + 1
                hora_in = datetime.now().strftime("%H:%M")
                # Envia para Produção
                nova_p = pd.DataFrame([[id_os, cli, med, serv, hora_in, "--:--", "Em Produção", ""]], columns=st.session_state.producao.columns)
                st.session_state.producao = pd.concat([st.session_state.producao, nova_p], ignore_index=True)
                # Envia para Financeiro
                nova_f = pd.DataFrame([[datetime.now().strftime("%d/%m"), f"Serviço {id_os}: {cli}", "Entrada", val]], columns=st.session_state.financeiro.columns)
                st.session_state.financeiro = pd.concat([st.session_state.financeiro, nova_f], ignore_index=True)
                st.success(f"OS {id_os} criada com sucesso!")

# --- 🏭 PRODUÇÃO ---
elif menu == "🏭 Produção":
    st.header("🏭 Ficha de Produção (Editável)")
    st.session_state.producao = st.data_editor(st.session_state.producao, num_rows="dynamic", use_container_width=True)

# --- 📦 ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)

# --- 💰 FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.header("💰 Financeiro")
    st.session_state.financeiro = st.data_editor(st.session_state.financeiro, num_rows="dynamic", use_container_width=True)

# --- ⚙️ EMPRESA ---
elif menu == "⚙️ Empresa":
    st.header("⚙️ Cadastro da Empresa")
    st.text_input("CNPJ", "00.000.000/0001-00")
    st.text_input("Endereço", "Rua...")
    st.text_input("Telefone", "(00) 00000-0000")

# --- 📊 PAINEL GERAL ---
else:
    st.title(f"📊 Painel Geral - {emp_nome}")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("⚙️ Oficina Ativa")
        st.dataframe(st.session_state.producao[st.session_state.producao['Status'] != 'Finalizado'], use_container_width=True)
    with c2:
        st.subheader("📦 Alerta Estoque")
        st.dataframe(st.session_state.estoque[st.session_state.estoque['Qtd'] < 5], use_container_width=True)
    with c3:
        st.subheader("💰 Caixa")
        ent = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Entrada']['Valor'].sum()
        sai = st.session_state.financeiro[st.session_state.financeiro['Tipo'] == 'Saída']['Valor'].sum()
        st.metric("Saldo", f"R$ {ent-sai:,.2f}")



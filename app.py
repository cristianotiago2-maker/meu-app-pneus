
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


---------- Forwarded message ---------
De: Tiago Cristiano da Silva <cristianotiago2@gmail.com>
Date: sex., 17 de abr. de 2026, 19:54
Subject:
To: Tiago Cristiano da Silva <cristianotiago2@gmail.com>


import streamlit as st
import pandas as pd

# Configuração visual do sistema
st.set_page_config(page_title="Vulcat Pneus - Gestão", page_icon="🚛", layout="wide")

# Estilo para deixar os cards bonitos
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007BFF; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.image("https://flaticon.com", width=100)
st.sidebar.title("VULCAT PNEUS")
menu = st.sidebar.radio("Navegação Principal", 
    ["📊 Painel Geral", "📝 Gerar Orçamento", "🏭 Ficha de Produção", "📦 Estoque Pesado", "💰 Financeiro"])

# --- 1. PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title("📊 Painel Geral de Operações")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Serviços Ativos", "08", "🔄")
    c2.metric("Prontos p/ Entrega", "03", "✅")
    c3.metric("Faturamento Mês", "R$ 12.450", "+5%")
    c4.metric("Alertas Estoque", "2 itens", "⚠️", delta_color="inverse")
    
    st.subheader("🚚 Status de Produção em Tempo Real")
    st.info("🚛 Scania R450 (Placa: ABC-1234) - Status: **VULCANIZAÇÃO**")
    st.warning("🚜 Trator John Deere (Fazenda Sol) - Status: **AGUARDANDO REPARO**")

# --- 2. ORÇAMENTOS ---
elif menu == "📝 Gerar Orçamento":
    st.title("📝 Novo Orçamento - Vulcat Pneus")
    with st.form("orcamento"):
        col1, col2 = st.columns(2)
        cliente = col1.text_input("Cliente / Empresa")
        veiculo = col2.text_input("Veículo / Placa")
        
        medida = st.selectbox("Medida do Pneu", [
            "295/80 R22.5 (Caminhão)", "275/80 R22.5 (Caminhão)", "11.00 R22 (Caminhão)",
            "18.4-34 (Trator)", "23.1-26 (Trator)", "14.9-24 (Trator)", "7.50-16 (F4000)"
        ])
        
        servico = st.multiselect("Serviços Requeridos", 
            ["Vulcanização Lateral", "Recapagem", "Conserto de Talão", "Manchão a Quente", "Montagem"])
        
        valor = st.number_input("Valor Total do Orçamento (R$)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Gerar e Salvar Orçamento"):
            st.success(f"Orçamento para {cliente} registrado com sucesso!")

# --- 3. FICHA DE PRODUÇÃO (SEM VALORES) ---
elif menu == "🏭 Ficha de Produção":
    st.title("🏭 Ficha de Trabalho - Oficina")
    st.caption("Visualização restrita para produção (Valores ocultos)")
    
    dados_oficina = pd.DataFrame({
        "OS": ["#502", "#503", "#504"],
        "Cliente": ["Logística Brasil", "Fazenda Rio Doce", "TransPneus"],
        "Medida": ["295/80 R22.5", "18.4-34", "275/80 R22.5"],
        "Serviço": ["Vulcanização", "Reparo Agrícola", "Recapagem"],
        "Etapa": ["Limpeza", "Aplicação de Cola", "Autoclave"]
    })
    st.table(dados_oficina)

# --- 4. ESTOQUE ---
elif menu == "📦 Estoque Pesado":
    st.title("📦 Controle de Estoque (Carga e Tratores)")
    t1, t2 = st.tabs(["Pneus Novos/Usados", "Insumos"])
    
    with t1:
        st.write("Estoque de Carcaças e Pneus")
        st.dataframe(pd.DataFrame({
            "Medida": ["295/80", "18.4-34", "11.00-22"],
            "Qtd": [12, 4, 7],
            "Tipo": ["Caminhão", "Trator", "Caminhão"]
        }))
        
    with t2:
        st.write("Insumos de Vulcanização")
        st.progress(0.2, "Cola (Crítico)")
        st.progress(0.8, "Manchões (Ok)")

# --- 5. FINANCEIRO ---
elif menu == "💰 Financeiro":
    st.title("💰 Gestão Financeira - Vulcat Pneus")
    st.subheader("Fluxo de Caixa")
    st.area_chart([12000, 15000, 11000, 18000, 14000]) # Exemplo de gráfico
    
    st.write("Contas a Receber: **R$ 8.500,00**")
    st.write("Contas a Pagar: **R$ 3.200,00**")



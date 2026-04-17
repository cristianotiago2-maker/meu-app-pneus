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

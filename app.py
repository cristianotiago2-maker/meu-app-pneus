import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Vulcat Pneus", page_icon="🛞", layout="wide")

# 2. BARRA LATERAL (CONFIGURAÇÕES DA EMPRESA)
with st.sidebar:
    st.header("🏢 Dados da Empresa")
    # Logotipo
    try:
        st.image("logo.png", width=150)
    except:
        st.info("Suba o 'logo.png' no GitHub")
    
    # Informações Editáveis
    nome_app = st.text_input("Nome do Sistema", "Vulcat Pneus")
    icone_topo = st.text_input("Ícone do Topo (Emoji)", "🚜")
    cnpj = st.text_input("CNPJ", "00.000.000/0001-00")
    endereco = st.text_area("Endereço", "Rua Exemplo, 123")
    telefone = st.text_input("Telefone/WhatsApp", "(00) 00000-0000")
    
    st.divider()
    st.caption(f"{nome_app} - v2.0")

# 3. CABEÇALHO DINÂMICO
st.title(f"{icone_topo} {nome_app}")
st.write(f"**CNPJ:** {cnpj} | **Tel:** {telefone}")

# 4. ABAS DE NAVEGAÇÃO (Para não poluir o visual)
aba1, aba2, aba3, aba4 = st.tabs(["📋 Orçamento Pneus", "👥 Clientes", "📦 Estoque", "📸 Recibos"])

# --- ABA 1: ORÇAMENTO ESPECÍFICO DE PNEUS ---
with aba1:
    st.subheader("📝 Orçamento Detalhado de Pneus")
    
    # Tabela editável com campos específicos para pneus
    dados_pneus = {
        "Frota/Veículo": ["Caminhão 01", "Trator 05"],
        "Medida do Pneu": ["295/80 R22.5", "18.4-34"],
        "Serviço": ["Recapagem", "Conserto"],
        "Qtd": [1, 1],
        "Valor Unit. (R$)": [0.0, 0.0]
    }
    df_pneus = pd.DataFrame(dados_pneus)
    
    grid_pneus = st.data_editor(df_pneus, num_rows="dynamic", use_container_width=True, key="pneus_edit")
    
    total_pneus = (grid_pneus["Qtd"] * grid_pneus["Valor Unit. (R$)"]).sum()
    st.metric("Total do Orçamento", f"R$ {total_pneus:,.2f}")
    
    if st.button("📄 Gerar PDF do Orçamento"):
        st.info("Função de exportação PDF pronta. (Simulada: Os dados foram processados para impressão)")

# --- ABA 2: CLIENTES ---
with aba2:
    st.subheader("👥 Cadastro de Clientes")
    df_clientes = pd.DataFrame({"Nome/Razão Social": [""], "CPF/CNPJ": [""], "Contato": [""]})
    st.data_editor(df_clientes, num_rows="dynamic", use_container_width=True)

# --- ABA 3: ESTOQUE ---
with aba3:
    st.subheader("📦 Controle de Estoque")
    df_estoque = pd.DataFrame({"Produto": ["Pneu Novo", "Banda de Rodagem"], "Estoque Atual": [0], "Minimo": [5]})
    st.data_editor(df_estoque, num_rows="dynamic", use_container_width=True)

# --- ABA 4: FOTOS ---
with aba4:
    st.subheader("📸 Notas e Comprovantes")
    fotos = st.file_uploader("Anexar arquivos", type=['png', 'jpg', 'pdf'], accept_multiple_files=True)
    if fotos:
        cols = st.columns(4)
        for i, f in enumerate(fotos):
            with cols[i % 4]:
                st.image(f, use_container_width=True)

# 5. RODAPÉ DE IMPRESSÃO
st.divider()
if st.button("🖨️ Modo de Impressão (Visualizar PDF)"):
    st.write(f"### {nome_app}")
    st.write(f"Endereço: {endereco}")
    st.write(f"Dados do Orçamento: {datetime.now().strftime('%d/%m/%Y')}")
    st.table(grid_pneus)
















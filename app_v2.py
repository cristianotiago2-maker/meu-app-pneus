import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Agro-Frota v2", layout="wide")

# --- 1. LOGOTIPO E CONFIGURAÇÃO DA EMPRESA ---
with st.sidebar:
    # Tenta carregar o logo se o arquivo existir no GitHub
    try:
        st.image("logo.png", width=200)
    except:
        st.warning("⚠️ Adicione o arquivo 'logo.png' no GitHub.")
    
    st.title("Configurações")
    nome_empresa = st.text_input("Nome da Empresa", "Agro-Frota")
    st.divider()

st.title(f"📊 Painel: {nome_empresa}")

# --- 2. ORÇAMENTO COM ESPAÇO EDITÁVEL ---
st.subheader("📝 Planejamento de Orçamento")

# Criamos uma tabela base
dados_base = {
    "Descrição do Item": ["Combustível", "Manutenção", "Pneus", "Seguro"],
    "Valor Planejado (R$)": [0.0, 0.0, 0.0, 0.0]
}
df_orcamento = pd.DataFrame(dados_base)

# Tabela Editável (Aqui você pode escrever e mudar os valores)
tabela_editavel = st.data_editor(
    df_orcamento, 
    num_rows="dynamic", # Permite adicionar ou excluir linhas
    use_container_width=True
)

total = tabela_editavel["Valor Planejado (R$)"].sum()
st.metric("Total Geral do Orçamento", f"R$ {total:,.2f}")

# --- 3. ANEXAR NOTAS FISCAIS ---
st.divider()
st.subheader("📸 Anexar Notas e Recibos")
fotos = st.file_uploader("Tire foto ou escolha o arquivo", type=['png', 'jpg', 'jpeg', 'pdf'], accept_multiple_files=True)

if fotos:
    cols = st.columns(3)
    for i, foto in enumerate(fotos):
        with cols[i % 3]:
            st.image(foto, caption=foto.name, use_container_width=True)

st.divider()
st.info("💡 Lembrete: Por enquanto, as alterações somem ao fechar o app. No próximo passo, vamos configurar para salvar de verdade.")


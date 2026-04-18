import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA BARRA LATERAL (LOGO E NOME)
with st.sidebar:
    try:
        # Tenta carregar a imagem 'logo.png' que você vai subir no GitHub
        st.image("logo.png", width=200)
    except:
        st.info("💡 Para ver seu logo aqui, suba um arquivo chamado 'logo.png' no GitHub.")
    
    st.divider()
    st.title("⚙️ Configurações")
    nome_empresa = st.text_input("Nome da Empresa", "Agro-Frota")

# 2. TÍTULO PRINCIPAL
st.title(f"🚜 Gestão: {nome_empresa}")

# 3. ÁREA DE ORÇAMENTO EDITÁVEL
st.divider()
st.subheader("📝 Orçamento e Metas")
st.write("Clique nas células abaixo para editar os valores:")

# Criando a tabela inicial
dados = {
    "Categoria": ["Diesel", "Manutenção Preventiva", "Pneus", "Seguros", "Outros"],
    "Valor Planejado (R$)": [0.0, 0.0, 0.0, 0.0, 0.0]
}
df_base = pd.DataFrame(dados)

# O data_editor permite que você mude os valores direto no app
tabela_editavel = st.data_editor(
    df_base, 
    num_rows="dynamic", # Permite adicionar e excluir linhas (botão +)
    use_container_width=True
)

# Calcula o total automaticamente conforme você edita
total = tabela_editavel["Valor Planejado (R$)"].sum()
st.metric("Total do Orçamento", f"R$ {total:,.2f}")

# 4. ANEXAR NOTAS FISCAIS (SUPORTE A FOTOS)
st.divider()
st.subheader("📸 Notas Fiscais e Recibos")
st.write("Tire uma foto ou anexe documentos abaixo:")

arquivos = st.file_uploader(
    "Selecionar arquivos", 
    type=['png', 'jpg', 'jpeg', 'pdf'], 
    accept_multiple_files=True
)

if arquivos:
    # Mostra as fotos em colunas
    colunas = st.columns(3)
    for index, arquivo in enumerate(arquivos):
        with colunas[index % 3]:
            if arquivo.type != "application/pdf":
                st.image(arquivo, caption=arquivo.name, use_container_width=True)
            else:
                st.write(f"📄 {arquivo.name}")

st.divider()
st.warning("⚠️ Lembre-se: Por enquanto, ao atualizar a página (F5), os dados voltam ao padrão. O próximo passo será configurar o Google Sheets para salvar fixo.")




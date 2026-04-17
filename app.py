import streamlit as st

st.set_page_config(page_title="Educat Pneus", page_icon="🛞")
st.title("🛞 Sistema Educat Pneus")

with st.form("venda"):
    cliente = st.text_input("Nome do Cliente")
    placa = st.text_input("Placa do Veículo")
    servico = st.selectbox("Serviço", ["Vulcanização", "Troca", "Alinhamento"])
    valor = st.number_input("Valor R$", min_value=0.0)
    enviar = st.form_submit_button("Registrar")
    
    if enviar:
        st.success(f"Registrado: {cliente} - {servico} - R$ {valor}")

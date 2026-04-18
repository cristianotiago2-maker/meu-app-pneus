import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

ARQUIVO = "controle_borracharia.xlsx"
st.set_page_config(page_title="Borracharia Pro", layout="wide", page_icon="🛞")

# CSS pra deixar moderno
st.markdown("""
<style>
    .main > div {padding-top: 1rem;}
    .stMetric {background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333;}
</style>
""", unsafe_allow_html=True)

def init_db():
    if not os.path.exists(ARQUIVO):
        dfs = {
            "Orcamentos": pd.DataFrame(columns=["ID","Data","Cliente","Placa","Medida","Servico","Valor","Status"]),
            "OS": pd.DataFrame(columns=["ID","Data_Abertura","Cliente","Placa","Medida","Servico","Valor","Status_Producao","Pago","Forma_Pgto","Data_Pgto"]),
            "Producao": pd.DataFrame(columns=["ID_OS","Data_Fim","Responsavel","Material_Usado","Qtd_Material","Tempo_Min"]),
            "Estoque": pd.DataFrame(columns=["ID","Item","Qtd","Unidade","Valor_Unit","Estoque_Min","Ultima_Entrada"])
        }
        with pd.ExcelWriter(ARQUIVO, engine='openpyxl') as writer:
            for nome, df in dfs.items():
                df.to_excel(writer, sheet_name=nome, index=False)

@st.cache_data
def load_data():
    return {aba: pd.read_excel(ARQUIVO, sheet_name=aba) for aba in ["Orcamentos","OS","Producao","Estoque"]}

def save_data(dados):
    with pd.ExcelWriter(ARQUIVO, engine='openpyxl') as writer:
        for aba, df in dados.items():
            df.to_excel(writer, sheet_name=aba, index=False)
    st.cache_data.clear()

init_db()
dados = load_data()

st

import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF
from datetime import datetime

# 1. CONFIGURAÇÃO E ESTILO (DESIGN TOP)
st.set_page_config(page_title="AgroFrota ERP", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 32px; color: #00ffa2; font-weight: bold; }
    .stPlotlyChart { border-radius: 15px; overflow: hidden; }
    .card-topo {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border-top: 5px solid #00ffa2;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS
def get_connection():
    return sqlite3.connect('agrofrota_vfinal.db', check_same_thread=False)

# 3. MENU LATERAL
with st.sidebar:
    st.markdown("<h1 style='color: #00ffa2;'>🚜 AGRO-FROTA</h1>", unsafe_allow_html=True)
    menu = st.selectbox("Navegação", ["📊 Dashboard", "🛞 Estoque Pneus", "👥 Clientes", "🛠️ Produção"])

# 4. MÓDULO DASHBOARD (ITENS EM CIMA + PIZZA EMBAIXO)
if menu == "📊 Dashboard":
    st.title("📊 Resumo Operacional")
    
    # --- PARTE DE CIMA: ITENS (METRICS) ---
    conn = get_connection()
    df_pneus = pd.read_sql("SELECT tipo, qtd FROM pneus", conn)
    total_cli = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn)['total'].iloc[0]
    conn.close()

    total_estoque = df_pneus['qtd'].sum() if not df_pneus.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Estoque Total", f"{total_estoque} un")
    col2.metric("Clientes", total_cli)
    col3.metric("O.S. Ativas", "12")
    col4.metric("Produtividade", "92%")

    st.write("---")

    # --- PARTE DE BAIXO: GRÁFICO DE PIZZA ---
    st.subheader("🎯 Distribuição de Estoque")
    
    if not df_pneus.empty:
        # Agrupa para o gráfico de pizza
        pizza_data = df_pneus.groupby('tipo')['qtd'].sum()
        # Usando o gráfico nativo do Streamlit para pizza via mapeamento de cores
        st.write("Proporção: Agrícola vs Rodoviário")
        
        # Criando colunas para centralizar o gráfico
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            # Mostra uma tabela visual ou gráfico dependendo da biblioteca disponível
            # Aqui usamos o st.pie_chart se disponível ou simulamos com barras circulares
            import plotly.express as px
            fig = px.pie(df_pneus, values='qtd', names='tipo', 
                         color_discrete_sequence=['#00ffa2', '#00aaff'],
                         hole=0.4)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cadastre pneus no estoque para visualizar o gráfico de pizza.")

# 5. MÓDULOS DE CADASTRO (Simplificados para manter o foco no Dashboard)
elif menu == "🛞 Estoque Pneus":
    st.title("🛞 Cadastro de Estoque")
    with st.form("pneus"):
        t = st.selectbox("Tipo", ["Agrícola", "Rodoviário"])
        m = st.text_input("Marca")
        q = st.number_input("Quantidade", min_value=1)
        if st.form_submit_button("Salvar"):
            c = get_connection()
            c.execute("INSERT INTO pneus (tipo, marca, qtd) VALUES (?,?,?)", (t, m, q))
            c.commit()
            st.rerun()

elif menu == "👥 Clientes":
    st.title("👥 Clientes")
    # ... código de clientes ...

elif menu == "🛠️ Produção":
    st.title("🛠️ Produção")
    # ... código de produção ...








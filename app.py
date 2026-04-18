import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO DE ESTADO PARA CORES ---
if 'cor_primaria' not in st.session_state:
    st.session_state.cor_primaria = "#0099aa"  # Cor padrão inicial

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Pneus PRO | Customizado", layout="wide")

# CSS DINÂMICO (Usa a cor escolhida pelo usuário)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f7f6; }}
    
    /* Estilo dos Cards Baseado na Cor Escolhida */
    .card {{
        background: #262730;
        color: white;
        padding: 20px;
        border-radius: 15px;
        flex: 1;
        text-align: center;
        border-bottom: 5px solid {st.session_state.cor_primaria};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .card h2 {{ color: {st.session_state.cor_primaria}; margin-top: 10px; }}
    
    .card-container {{
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
conn = sqlite3.connect('pneus_custom.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY, tipo TEXT, cat TEXT, valor REAL)')
c.execute('CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY, medida TEXT, qtd INTEGER)')
conn.commit()

# --- MENU SUPERIOR CUSTOMIZADO ---
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Financeiro", "Estoque", "Produção", "Configurações"],
    icons=["grid-fill", "wallet2", "box-seam", "truck", "gear"],
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffffff"},
        "nav-link-selected": {"background-color": st.session_state.cor_primaria},
    }
)

# --- LÓGICA DE DADOS ---
df_fin = pd.read_sql('SELECT * FROM financeiro', conn)
rec = df_fin[df_fin['tipo'] == 'Entrada']['valor'].sum()
desp = df_fin[df_fin['tipo'] == 'Saída']['valor'].sum()

# --- NAVEGAÇÃO ---

if selected == "Dashboard":
    st.markdown(f"### 🚀 Painel de Controle - <span style='color:{st.session_state.cor_primaria}'>Gestão Ativa</span>", unsafe_allow_html=True)
    
    # Cards que mudam de cor conforme a escolha
    st.markdown(f"""
        <div class="card-container">
            <div class="card">
                <h3>💰 Saldo Atual</h3>
                <h2>R$ {rec-desp:,.2f}</h2>
            </div>
            <div class="card">
                <h3>📈 Entradas</h3>
                <h2>R$ {rec:,.2f}</h2>
            </div>
            <div class="card">
                <h3>📉 Saídas</h3>
                <h2>R$ {desp:,.2f}</h2>
            </div>
            <div class="card">
                <h3>📦 Itens Estoque</h3>
                <h2>{len(pd.read_sql('SELECT * FROM estoque', conn))}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df_fin, x="cat", y="valor", color="tipo", barmode="group", 
                     color_discrete_sequence=[st.session_state.cor_primaria, "#ff6347"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.pie(df_fin, values='valor', names='cat', hole=0.5)
        st.plotly_chart(fig2, use_container_width=True)

elif selected == "Configurações":
    st.title("⚙️ Personalização do Sistema")
    
    st.subheader("🎨 Identidade Visual")
    nova_cor = st.color_picker("Escolha a cor principal do seu sistema", st.session_state.cor_primaria)
    
    if st.button("Aplicar Nova Cor"):
        st.session_state.cor_primaria = nova_cor
        st.rerun()

    st.markdown("---")
    st.subheader("🏢 Informações da Empresa")
    col1, col2 = st.columns(2)
    nome_emp = col1.text_input("Nome da Empresa", "Pneus Pro")
    cnpj_emp = col2.text_input("CNPJ", "00.000.000/0001-00")
    logo = st.file_uploader("Carregar Logotipo")

# --- Módulos Financeiro, Estoque e Produção mantêm a lógica anterior ---
elif selected == "Financeiro":
    st.title("💸 Financeiro")
    with st.form("fin"):
        t = st.selectbox("Tipo", ["Entrada", "Saída"])
        cat = st.text_input("Categoria (Venda, Aluguel, etc)")
        val = st.number_input("Valor")
        if st.form_submit_button("Salvar"):
            c.execute('INSERT INTO financeiro (tipo, cat, valor) VALUES (?,?,?)', (t, cat, val))
            conn.commit()
            st.rerun()
    st.dataframe(df_fin, use_container_width=True)

elif selected == "Estoque":
    st.title("🛞 Estoque")
    df_est = pd.read_sql('SELECT * FROM estoque', conn)
    ed = st.data_editor(df_est, num_rows="dynamic", use_container_width=True)
    if st.button("Sincronizar"):
        ed.to_sql('estoque', conn, if_exists='replace', index=False)
        st.success("Salvo!")

elif selected == "Produção":
    st.title("🛠️ Produção")
    cli = st.text_input("Cliente")
    serv = st.text_area("Descrição do Serviço")
    if st.button("Gerar Ficha"):
        st.info("Gerando PDF com a identidade visual selecionada...")
        # Lógica de PDF aqui...



import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF
from datetime import datetime
import plotly.express as px

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="ERP Pneus Pro + Alertas", layout="wide")

# --- CONEXÃO BANCO DE DADOS ---
conn = sqlite3.connect('dados_v3.db', check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY, data TEXT, descricao TEXT, tipo TEXT, categoria TEXT, valor REAL)')
c.execute('CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY, tipo_pneu TEXT, medida TEXT, marca TEXT, qtd INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, cnpj TEXT, nome TEXT, telefone TEXT)')
conn.commit()

def carregar(tabela):
    return pd.read_sql(f'SELECT * FROM {tabela}', conn)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://flaticon.com", width=100)
    st.title("Pneus System Pro")
    empresa = st.text_input("Sua Empresa", "Borracharia Inovação")
    cnpj_emp = st.text_input("CNPJ", "00.000.000/0001-00")
    st.markdown("---")
    menu = st.radio("Menu", ["Painel Geral", "Financeiro", "Produção", "Estoque", "Clientes"])
    qtd_minima = st.slider("Alerta de estoque mínimo", 1, 10, 3)

# --- MÓDULO 1: PAINEL GERAL (DASHBOARD + ALERTAS) ---
if menu == "Painel Geral":
    st.title(f"📊 Dashboard - {empresa}")
    
    # --- ÁREA DE ALERTAS ---
    df_est = carregar("estoque")
    if not df_est.empty:
        estoque_baixo = df_est[df_est['qtd'] <= qtd_minima]
        if not estoque_baixo.empty:
            for _, row in estoque_baixo.iterrows():
                st.error(f"🚨 **ALERTA DE ESTOQUE:** O pneu **{row['medida']} ({row['marca']})** tem apenas **{row['qtd']}** unidades!")

    # --- MÉTRICAS FINANCEIRAS ---
    df_fin = carregar("financeiro")
    col1, col2, col3 = st.columns(3)
    
    if not df_fin.empty:
        rec = df_fin[df_fin['tipo'] == 'Entrada']['valor'].sum()
        desp = df_fin[df_fin['tipo'] == 'Saída']['valor'].sum()
        col1.metric("Receita Total", f"R$ {rec:,.2f}")
        col2.metric("Despesas", f"R$ {desp:,.2f}", delta=f"-{desp:,.2f}", delta_color="inverse")
        col3.metric("Caixa Líquido", f"R$ {rec-desp:,.2f}")

        st.markdown("---")
        g1, g2 = st.columns(2)
        
        with g1:
            st.subheader("Entradas por Categoria")
            df_e = df_fin[df_fin['tipo'] == 'Entrada']
            fig_e = px.pie(df_e, values='valor', names='categoria', hole=.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_e, use_container_width=True)
            
        with g2:
            st.subheader("Saídas por Categoria")
            df_s = df_fin[df_fin['tipo'] == 'Saída']
            fig_s = px.pie(df_s, values='valor', names='categoria', hole=.4, color_discrete_sequence=px.colors.sequential.YlOrRd)
            st.plotly_chart(fig_s, use_container_width=True)

# --- MÓDULO 2: FINANCEIRO COMPLETO ---
elif menu == "Financeiro":
    st.title("💸 Fluxo de Caixa Detalhado")
    with st.expander("Registrar Movimentação"):
        c1, c2, c3, c4 = st.columns(4)
        d = c1.text_input("Descrição")
        v = c2.number_input("Valor R$", 0.0)
        t = c3.selectbox("Tipo", ["Entrada", "Saída"])
        cat = c4.selectbox("Categoria", ["Serviço", "Venda", "Compra Estoque", "Luz/Água", "Salários"])
        if st.button("Lançar"):
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            c.execute('INSERT INTO financeiro (data, descricao, tipo, categoria, valor) VALUES (?,?,?,?,?)', (data_hoje, d, t, cat, v))
            conn.commit()
            st.success("Lançado com sucesso!")
            st.rerun()
    
    st.data_editor(carregar("financeiro"), use_container_width=True)

# --- MÓDULO 3: PRODUÇÃO ---
elif menu == "Produção":
    st.title("🏗️ Ordem de Serviço")
    with st.form("os"):
        cli = st.text_input("Cliente")
        med = st.text_input("Medidas dos Pneus")
        serv = st.selectbox("Serviço", ["Recapagem", "Rodoviário", "Agrícola", "Reparo"])
        obs = st.text_area("Observações Técnicas")
        if st.form_submit_button("Gerar Ficha"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, empresa, ln=1, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, f"FICHA TÉCNICA - {serv}", ln=1, align='C')
            pdf.ln(10)
            pdf.cell(0, 10, f"Cliente: {cli} | Medidas: {med}", ln=1)
            pdf.multi_cell(0, 10, f"Instruções: {obs}")
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("Clique para Baixar PDF", pdf_bytes, "ficha_producao.pdf")

# --- MÓDULO 4: ESTOQUE EDITÁVEL ---
elif menu == "Estoque":
    st.title("🛞 Inventário de Pneus")
    st.caption("Dica: Use a última linha vazia para adicionar novos itens.")
    df_est = carregar("estoque")
    df_edit = st.data_editor(df_est, use_container_width=True, num_rows="dynamic")
    
    if st.button("Sincronizar Estoque"):
        df_edit.to_sql('estoque', conn, if_exists='replace', index=False)
        st.success("Estoque atualizado!")
        st.rerun()

# --- MÓDULO 5: CLIENTES ---
elif menu == "Clientes":
    st.title("👥 Carteira de Clientes")
    df_cli = carregar("clientes")
    df_cli_ed = st.data_editor(df_cli, use_container_width=True, num_rows="dynamic")
    if st.button("Salvar Clientes"):
        df_cli_ed.to_sql('clientes', conn, if_exists='replace', index=False)
        st.success("Salvo!")

from fpdf import FPDF
import datetime

elif menu == "Ficha Produção":
    st.title("📋 FICHA DE PRODUÇÃO")

    cliente = st.text_input("Cliente")
    veiculo = st.text_input("Veículo")
    servico = st.text_area("Serviço realizado")

    if st.button("Gerar PDF"):
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="FICHA DE PRODUÇÃO", ln=True, align="C")
        pdf.ln(10)

        pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
        pdf.cell(200, 10, txt=f"Veículo: {veiculo}", ln=True)
        pdf.multi_cell(200, 10, txt=f"Serviço: {servico}")

        data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Data: {data}", ln=True)

        file_name = "ficha_producao.pdf"
        pdf.output(file_name)

        with open(file_name, "rb") as f:
            st.download_button(
                label="📥 Baixar PDF",
                data=f,
                file_name=file_name,
                mime="application/pdf"
            )

        st.success("PDF gerado com sucesso!")

---------- Forwarded message ---------
De: Tiago Cristiano da Silva <cristianotiago2@gmail.com>
Date: sáb., 18 de abr. de 2026, 00:22
Subject: Fwd:
To: Tiago Cristiano da Silva <cristianotiago2@gmail.com>


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


---------- Forwarded message ---------
De: Tiago Cristiano da Silva <cristianotiago2@gmail.com>
Date: sáb., 18 de abr. de 2026, 00:04
Subject: Fwd:
To: Tiago Cristiano da Silva <cristianotiago2@gmail.com>


import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="Vulcanização PRO", layout="wide")

# ----------- ESTILO -----------
st.markdown("""
<style>
.main {background-color: #f5f7fa;}
h1 {color: #0e1117;}
.stButton>button {
    background-color: #0e1117;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ----------- LOGIN -----------
def login():
    st.markdown("## 🔐 Sistema Vulcanização")
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if user == "admin" and senha == "123":
                st.session_state.logado = True
            else:
                st.error("Login inválido")

# ----------- PDF -----------
def gerar_pdf(cliente, servico, valor):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 800, "ORÇAMENTO - VULCANIZAÇÃO")

    c.setFont("Helvetica", 12)
    c.drawString(100, 760, f"Cliente: {cliente}")
    c.drawString(100, 730, f"Serviço: {servico}")
    c.drawString(100, 700, f"Valor: R$ {valor}")

    c.save()
    buffer.seek(0)
    return buffer

# ----------- APP -----------
def app():
    st.title("🛞 Vulcanização PRO")

    menu = st.sidebar.radio("Menu", ["Dashboard", "Novo Serviço"])

    if "dados" not in st.session_state:
        st.session_state.dados = []

    # -------- DASHBOARD --------
    if menu == "Dashboard":
        st.subheader("📊 Visão Geral")

        if st.session_state.dados:
            df = pd.DataFrame(st.session_state.dados)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Serviços", len(df))

            with col2:
                st.metric("Faturamento", f"R$ {df['Valor'].sum():.2f}")

            with col3:
                st.metric("Ticket Médio", f"R$ {df['Valor'].mean():.2f}")

            st.divider()

            filtro = st.text_input("🔍 Buscar cliente")

            if filtro:
                df = df[df["Cliente"].str.contains(filtro, case=False)]

            st.dataframe(df, use_container_width=True)

        else:
            st.info("Nenhum serviço cadastrado")

    # -------- NOVO SERVIÇO --------
    if menu == "Novo Serviço":
        st.subheader("➕ Novo Atendimento")

        col1, col2 = st.columns(2)

        with col1:
            cliente = st.text_input("Cliente")
            servico = st.text_input("Serviço")

        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)

        if st.button("💾 Salvar"):
            st.session_state.dados.append({
                "Cliente": cliente,
                "Serviço": servico,
                "Valor": valor
            })
            st.success("Serviço cadastrado!")

        if st.button("📄 Gerar Orçamento"):
            pdf = gerar_pdf(cliente, servico, valor)

            st.download_button(
                "Baixar PDF",
                pdf,
                file_name="orcamento.pdf",
                mime="application/pdf"
            )

# -------- EXECUÇÃO --------
if "logado" not in st.session_state:
    st.session_state.logado = False

if st.session_state.logado:
    app()
else:
    login()

---------- Forwarded message ---------
De: Tiago Cristiano da Silva <cristianotiago2@gmail.com>
Date: sáb., 18 de abr. de 2026, 00:01
Subject:
To: Tiago Cristiano da Silva <cristianotiago2@gmail.com>


import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
import io

# ---------------- LOGIN ----------------
def login():
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == "admin" and senha == "123":
            st.session_state.logado = True
        else:
            st.error("Login inválido")

# ---------------- PDF ----------------
def gerar_pdf(cliente, servico, valor):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    c.drawString(100, 800, "VULCANIZAÇÃO")
    c.drawString(100, 760, f"Cliente: {cliente}")
    c.drawString(100, 740, f"Serviço: {servico}")
    c.drawString(100, 720, f"Valor: R$ {valor}")

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- APP ----------------
def app():
    st.title("🛞 Sistema de Vulcanização")

    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Novo Serviço"])

    if "dados" not in st.session_state:
        st.session_state.dados = []

    if menu == "Dashboard":
        st.subheader("📊 Serviços Realizados")

        if st.session_state.dados:
            df = pd.DataFrame(st.session_state.dados)
            st.dataframe(df)

            total = df["Valor"].sum()
            st.success(f"💰 Total: R$ {total}")

        else:
            st.info("Nenhum serviço cadastrado")

    if menu == "Novo Serviço":
        st.subheader("➕ Cadastrar Serviço")

        cliente = st.text_input("Cliente")
        servico = st.text_input("Serviço")
        valor = st.number_input("Valor", min_value=0.0)

        if st.button("Salvar"):
            st.session_state.dados.append({
                "Cliente": cliente,
                "Serviço": servico,
                "Valor": valor
            })
            st.success("Salvo com sucesso!")

        if st.button("Gerar PDF"):
            pdf = gerar_pdf(cliente, servico, valor)
            st.download_button(
                label="📄 Baixar PDF",
                data=pdf,
                file_name="orcamento.pdf",
                mime="application/pdf"
            )

# ---------------- EXECUÇÃO ----------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if st.session_state.logado:
    app()
else:
    login()


import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# 1. CONFIGURAÇÃO E MEMÓRIA DO APP
st.set_page_config(page_title="VULCAT PNEUS - GESTÃO TOTAL", layout="wide", page_icon="🛞")

if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone", "Endereço"])
if 'db_estoque' not in st.session_state:
    st.session_state.db_estoque = pd.DataFrame([{"Item": "Recapagem 295/80", "Qtd": 10}, {"Item": "Conserto Vulcanização", "Qtd": 50}])
if 'db_financeiro' not in st.session_state:
    st.session_state.db_financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])

# 2. FUNÇÕES DE FORMATAÇÃO E PDF
def format_cnpj(v):
    v = ''.join(filter(str.isdigit, v))
    if len(v) == 14: return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    return v

def format_tel(v):
    v = ''.join(filter(str.isdigit, v))
    if len(v) == 11: return f"({v[:2]}) {v[2:7]}-{v[7:]}"
    return v

def gerar_pdf_v2(empresa, cliente, itens, total, pgto, datas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, empresa['nome'].upper(), ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"CNPJ: {format_cnpj(empresa['cnpj'])} | Tel: {format_tel(empresa['tel'])}", ln=True, align="C")
    pdf.cell(0, 5, empresa['end'], ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "ORÇAMENTO DE SERVIÇOS", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"CLIENTE: {cliente}", ln=True)
    pdf.cell(0, 7, f"DATA ENTRADA: {datas['ent']} | PREVISÃO ENTREGA: {datas['sai']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 8, "Item/Serviço", 1); pdf.cell(30, 8, "Qtd", 1); pdf.cell(40, 8, "V. Unit", 1); pdf.cell(30, 8, "Subtotal", 1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    for _, r in itens.iterrows():
        sub = r['Qtd'] * r['V. Unit']
        pdf.cell(90, 8, str(r['Item/Serviço']), 1); pdf.cell(30, 8, str(r['Qtd']), 1); pdf.cell(40, 8, f"{r['V. Unit']:,.2f}", 1); pdf.cell(30, 8, f"{sub:,.2f}", 1)
        pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL: R$ {total:,.2f}", ln=True, align="R")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Forma de Pagamento: {pgto}", ln=True)
    pdf.ln(20)
    pdf.cell(0, 10, "____________________________________________________", ln=True, align="C")
    pdf.cell(0, 5, "ASSINATURA DO CLIENTE", ln=True, align="C")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# 3. SIDEBAR
with st.sidebar:
    st.title("⚙️ CONFIGURAÇÕES")
    logo_file = st.file_uploader("Logo da Empresa", type=['png', 'jpg'])
    nome_empresa = st.text_input("Empresa", "VULCAT PNEUS")
    cnpj_i = st.text_input("CNPJ (números)")
    tel_i = st.text_input("Telefone (números)")
    end_i = st.text_area("Endereço Completo")

# 4. DASHBOARD
st.title(f"🚜 {nome_empresa}")
with st.expander("📈 PAINEL GERAL", expanded=True):
    ent = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Saída"]['Valor'].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento", f"R$ {ent:,.2f}")
    c2.metric("Despesas", f"R$ {sai:,.2f}", delta_color="inverse")
    c3.metric("Saldo Líquido", f"R$ {(ent-sai):,.2f}")

# 5. ABAS
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "💰 Financeiro", "📦 Estoque", "👥 Clientes"])

with tabs[0]: # ABA ORÇAMENTO
    st.subheader("📝 Orçamento com Prévia e PDF")
    o1, o2 = st.columns(2)
    cliente_sel = o1.selectbox("Cliente", [""] + st.session_state.db_clientes['Nome'].tolist())
    d_ent = o2.date_input("Entrada", format="DD/MM/YYYY")
    d_sai = o2.date_input("Saída", format="DD/MM/YYYY")

    edit_orc = st.data_editor(pd.DataFrame([{"Item/Serviço": "", "Qtd": 1, "V. Unit": 0.0}]), num_rows="dynamic", use_container_width=True, key="ed_orc",
                             column_config={"Item/Serviço": st.column_config.SelectboxColumn("Item/Serviço", options=st.session_state.db_estoque['Item'].tolist())})
    
    total_orc = (edit_orc['Qtd'] * edit_orc['V. Unit']).sum()
    pgto = st.selectbox("Pagamento", ["PIX", "Dinheiro", "Cartão", "Boleto"])

    col_btn1, col_btn2 = st.columns(2)
    previa = col_btn1.checkbox("🔍 Ver Pré-visualização")
    
    if previa:
        st.markdown(f"""<div style="border:1px solid #000;padding:20px;background:white;color:black">
        <h2 style="text-align:center">{nome_empresa}</h2><hr>
        <p><b>Cliente:</b> {cliente_sel} | <b>Total:</b> R$ {total_orc:,.2f}</p>
        <p style="text-align:center;margin-top:40px">__________________________<br>Assinatura</p></div>""", unsafe_allow_html=True)

    if col_btn2.button("🚀 Gerar Arquivo PDF"):
        empresa_dados = {'nome': nome_empresa, 'cnpj': cnpj_i, 'tel': tel_i, 'end': end_i}
        datas = {'ent': d_ent.strftime('%d/%m/%Y'), 'sai': d_sai.strftime('%d/%m/%Y')}
        pdf_bytes = gerar_pdf_v2(empresa_dados, cliente_sel, edit_orc, total_orc, pgto, datas)
        st.download_button("📥 Baixar PDF Agora", data=pdf_bytes, file_name=f"Orcamento_{cliente_sel}.pdf", mime="application/pdf")

with tabs[1]: # PRODUÇÃO
    st.data_editor(pd.DataFrame([{"OS": "", "Pneu": "", "Etapa": "Inspeção"}]), num_rows="dynamic", use_container_width=True)

with tabs[2]: # FINANCEIRO
    st.session_state.db_financeiro = st.data_editor(st.session_state.db_financeiro, num_rows="dynamic", use_container_width=True, column_config={"Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"), "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Entrada", "Saída"])})

with tabs[3]: # ESTOQUE
    st.session_state.db_estoque = st.data_editor(st.session_state.db_estoque, num_rows="dynamic", use_container_width=True)

with tabs[4]: # CLIENTES
    st.session_state.db_clientes = st.data_editor(st.session_state.db_clientes, num_rows="dynamic", use_container_width=True)











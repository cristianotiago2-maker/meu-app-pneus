import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# 1. CONFIGURAÇÃO E MEMÓRIA (Mantendo o que já funcionava)
st.set_page_config(page_title="VULCAT PNEUS - SISTEMA PRO", layout="wide", page_icon="🛞")

if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone", "Endereço"])
if 'db_estoque' not in st.session_state:
    st.session_state.db_estoque = pd.DataFrame(columns=["Item", "Qtd"])
if 'db_financeiro' not in st.session_state:
    st.session_state.db_financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])
if 'db_medidas' not in st.session_state:
    st.session_state.db_medidas = pd.DataFrame(columns=["Medida", "Quantidade", "Marca/Modelo"])
if 'bloco_notas' not in st.session_state:
    st.session_state.bloco_notas = ""

# 2. FUNÇÕES DE SUPORTE (MÁSCARAS E PDF)
def format_cnpj(v):
    v = ''.join(filter(str.isdigit, v))
    return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}" if len(v) == 14 else v

def format_tel(v):
    v = ''.join(filter(str.isdigit, v))
    return f"({v[:2]}) {v[2:7]}-{v[7:]}" if len(v) == 11 else v

def gerar_pdf_pro(empresa, cliente, itens, total, datas, logo_img=None):
    pdf = FPDF()
    pdf.add_page()
    if logo_img:
        img_temp = io.BytesIO()
        logo_img.save(img_temp, format="PNG")
        pdf.image(img_temp, 10, 8, 30)
        pdf.set_x(45)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, empresa['nome'].upper(), ln=True, align="L" if logo_img else "C")
    pdf.set_font("Arial", "", 10)
    pdf.set_x(45 if logo_img else 10)
    pdf.cell(0, 5, f"CNPJ: {format_cnpj(empresa['cnpj'])} | Tel: {format_tel(empresa['tel'])}", ln=True, align="L" if logo_img else "C")
    pdf.ln(20)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"CLIENTE: {cliente}", ln=True, border='B')
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 8, "Item/Medida", 1); pdf.cell(30, 8, "Qtd", 1); pdf.cell(50, 8, "V. Total", 1); pdf.ln()
    pdf.set_font("Arial", "", 10)
    for _, r in itens.iterrows():
        pdf.cell(100, 8, str(r['Item/Medida']), 1); pdf.cell(30, 8, str(r['Qtd']), 1); pdf.cell(50, 8, f"R$ {r['Valor']:,.2f}", 1); pdf.ln()
    pdf.ln(10); pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL: R$ {total:,.2f}", ln=True, align="R")
    pdf.ln(30); pdf.cell(0, 10, "________________________________________________", ln=True, align="C")
    pdf.cell(0, 5, "ASSINATURA DO CLIENTE", ln=True, align="C")
    return pdf.output()

# 3. SIDEBAR (LOGO DO COMPUTADOR)
with st.sidebar:
    st.title("⚙️ CONFIGURAÇÃO")
    up_logo = st.file_uploader("Subir Logotipo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    logo_img = Image.open(up_logo) if up_logo else None
    nome_empresa = st.text_input("Empresa", "VULCAT PNEUS")
    cnpj_i = st.text_input("CNPJ (números)")
    tel_i = st.text_input("Telefone (números)")
    empresa_dados = {'nome': nome_empresa, 'cnpj': cnpj_i, 'tel': tel_i}

# 4. PAINEL GERAL (GRÁFICOS PIZZA E MÉTRICAS)
st.title(f"📊 PAINEL GERAL - {nome_empresa}")
with st.expander("👁️ VISÃO GERAL (Métricas e Gráficos)", expanded=True):
    col_m1, col_m2, col_m3 = st.columns(3)
    ent = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Saída"]['Valor'].sum()
    col_m1.metric("Faturamento", f"R$ {ent:,.2f}")
    col_m2.metric("Despesas", f"R$ {sai:,.2f}", delta_color="inverse")
    col_m3.metric("Saldo Líquido", f"R$ {(ent-sai):,.2f}")
    
    st.divider()
    g1, g2 = st.columns(2)
    if ent > 0 or sai > 0:
        fig_fin = px.pie(values=[ent, sai], names=['Entradas', 'Saídas'], title="Saúde Financeira", hole=0.4, color_discrete_sequence=['#2ecc71', '#e74c3c'])
        g1.plotly_chart(fig_fin, use_container_width=True)
    if not st.session_state.db_estoque.empty:
        fig_est = px.pie(st.session_state.db_estoque, names='Item', values='Qtd', title="Distribuição de Estoque", hole=0.4)
        g2.plotly_chart(fig_est, use_container_width=True)

# 5. ABAS INTEGRADAS
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "🛞 Medidas/Pneus", "💰 Financeiro", "📦 Estoque", "👥 Clientes", "📝 Notas"])

with tabs[0]: # ORÇAMENTO
    st.subheader("Gerar Orçamento")
    cli_sel = st.selectbox("Escolher Cliente", [""] + st.session_state.db_clientes['Nome'].tolist())
    lista_itens = st.session_state.db_medidas['Medida'].tolist() + st.session_state.db_estoque['Item'].tolist()
    df_o = pd.DataFrame([{"Item/Medida": "", "Qtd": 1, "Valor": 0.0}])
    edit_orc = st.data_editor(df_o, num_rows="dynamic", use_container_width=True, column_config={"Item/Medida": st.column_config.SelectboxColumn("Item/Medida", options=lista_itens)})
    total_o = edit_orc['Valor'].sum()
    
    if st.checkbox("🔍 Pré-visualização"):
        st.markdown(f"<div style='border:1px solid #000;padding:20px;background:white;color:black'><h2 style='text-align:center'>{nome_empresa}</h2><hr><p><b>Cliente:</b> {cli_sel}</p><p style='text-align:center;margin-top:40px'>__________________________<br>Assinatura</p></div>", unsafe_allow_html=True)
    
    if st.button("🚀 Gerar PDF"):
        pdf_bytes = gerar_pdf_pro(empresa_dados, cli_sel, edit_orc, total_o, {}, logo_img)
        st.download_button("📥 Baixar PDF", data=bytes(pdf_bytes), file_name=f"Orcamento_{cli_sel}.pdf", mime="application/pdf")

with tabs[1]: st.subheader("🛠️ Produção"); st.data_editor(pd.DataFrame([{"OS": "", "Status": "Pendente"}]), num_rows="dynamic", use_container_width=True)
with tabs[2]: st.subheader("🛞 Cadastro de Medidas"); st.session_state.db_medidas = st.data_editor(st.session_state.db_medidas, num_rows="dynamic", use_container_width=True)
with tabs[3]: st.subheader("💰 Financeiro"); st.session_state.db_financeiro = st.data_editor(st.session_state.db_financeiro, num_rows="dynamic", use_container_width=True)
with tabs[4]: st.subheader("📦 Estoque"); st.session_state.db_estoque = st.data_editor(st.session_state.db_estoque, num_rows="dynamic", use_container_width=True)
with tabs[5]: st.subheader("👥 Clientes"); st.session_state.db_clientes = st.data_editor(st.session_state.db_clientes, num_rows="dynamic", use_container_width=True)
with tabs[6]: st.subheader("📝 Bloco de Notas"); st.session_state.bloco_notas = st.text_area("Anotações:", value=st.session_state.bloco_notas, height=300)







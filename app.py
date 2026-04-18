import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# 1. CONFIGURAÇÃO E MEMÓRIA DO APP
st.set_page_config(page_title="VULCAT PNEUS - GESTÃO PRO", layout="wide", page_icon="🛞")

# Estilização para um design mais robusto
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #FF4B4B; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 16px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone", "Endereço"])
if 'db_estoque' not in st.session_state:
    st.session_state.db_estoque = pd.DataFrame([{"Item": "Recapagem 295/80", "Qtd": 10}])
if 'db_financeiro' not in st.session_state:
    st.session_state.db_financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])
if 'db_medidas' not in st.session_state:
    st.session_state.db_medidas = pd.DataFrame(columns=["Medida", "Modelo/Marca", "Quantidade"])
if 'notas' not in st.session_state:
    st.session_state.notas = ""

# 2. FUNÇÕES DE APOIO E PDF
def format_cnpj(v):
    v = ''.join(filter(str.isdigit, v))
    return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}" if len(v) == 14 else v

def format_tel(v):
    v = ''.join(filter(str.isdigit, v))
    return f"({v[:2]}) {v[2:7]}-{v[7:]}" if len(v) == 11 else v

def gerar_pdf_pro(empresa, cliente, itens, total, pgto, datas, logo_img=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Adiciona Logo no PDF se existir
    if logo_img:
        img_temp = io.BytesIO()
        logo_img.save(img_temp, format="PNG")
        pdf.image(img_temp, 10, 8, 33)
        pdf.set_x(45)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, empresa['nome'].upper(), ln=True, align="L" if logo_img else "C")
    pdf.set_font("Arial", "", 9)
    pdf.set_x(45 if logo_img else 10)
    pdf.cell(0, 5, f"CNPJ: {format_cnpj(empresa['cnpj'])} | Tel: {format_tel(empresa['tel'])}", ln=True, align="L" if logo_img else "C")
    pdf.set_x(45 if logo_img else 10)
    pdf.cell(0, 5, empresa['end'], ln=True, align="L" if logo_img else "C")
    
    pdf.ln(15)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "ORÇAMENTO DE SERVIÇOS", ln=True, align="C", border="B")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"CLIENTE: {cliente}", ln=True)
    pdf.cell(0, 7, f"DATA ENTRADA: {datas['ent']} | PREVISÃO ENTREGA: {datas['sai']}", ln=True)
    pdf.ln(5)
    
    # Tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 8, "Item/Serviço", 1, 0, "C", True)
    pdf.cell(20, 8, "Qtd", 1, 0, "C", True)
    pdf.cell(40, 8, "V. Unit", 1, 0, "C", True)
    pdf.cell(40, 8, "Subtotal", 1, 1, "C", True)
    
    pdf.set_font("Arial", "", 10)
    for _, r in itens.iterrows():
        sub = r['Qtd'] * r['V. Unit']
        pdf.cell(90, 8, str(r['Item/Serviço']), 1)
        pdf.cell(20, 8, str(r['Qtd']), 1, 0, "C")
        pdf.cell(40, 8, f"{r['V. Unit']:,.2f}", 1, 0, "R")
        pdf.cell(40, 8, f"{sub:,.2f}", 1, 1, "R")
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL GERAL: R$ {total:,.2f}", ln=True, align="R")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Forma de Pagamento: {pgto}", ln=True)
    
    pdf.ln(20)
    pdf.cell(0, 10, "________________________________________________", ln=True, align="C")
    pdf.cell(0, 5, "ASSINATURA DO CLIENTE", ln=True, align="C")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# 3. SIDEBAR
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÕES")
    uploaded_logo = st.file_uploader("Logo da Empresa (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    logo_img = Image.open(uploaded_logo) if uploaded_logo else None
    
    nome_empresa = st.text_input("Empresa", "VULCAT PNEUS")
    cnpj_i = st.text_input("CNPJ (números)")
    tel_i = st.text_input("Telefone (números)")
    end_i = st.text_area("Endereço Completo")

# 4. PAINEL GERAL (DASHBOARD)
st.title(f"🚜 {nome_empresa}")
with st.expander("📊 INDICADORES GERAIS", expanded=True):
    ent = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Saída"]['Valor'].sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento", f"R$ {ent:,.2f}")
    c2.metric("Despesas", f"R$ {sai:,.2f}", delta_color="inverse")
    c3.metric("Saldo Líquido", f"R$ {(ent-sai):,.2f}")
    c4.metric("Itens no Estoque", st.session_state.db_estoque['Qtd'].sum())

# 5. ABAS DO SISTEMA
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "🛞 Medidas/Pneus", "💰 Financeiro", "📦 Estoque", "👥 Clientes", "📝 Notas"])

with tabs[0]: # ORÇAMENTO
    st.subheader("📝 Orçamento com Logo e Prévia")
    o1, o2 = st.columns(2)
    cliente_sel = o1.selectbox("Cliente", [""] + st.session_state.db_clientes['Nome'].tolist())
    d_ent = o2.date_input("Entrada", format="DD/MM/YYYY")
    d_sai = o2.date_input("Saída", format="DD/MM/YYYY", key="sai_orc")

    # Comunicação com Estoque e Medidas
    lista_itens = st.session_state.db_estoque['Item'].tolist() + st.session_state.db_medidas['Medida'].tolist()
    
    edit_orc = st.data_editor(pd.DataFrame([{"Item/Serviço": "", "Qtd": 1, "V. Unit": 0.0}]), num_rows="dynamic", use_container_width=True, key="ed_orc",
                             column_config={"Item/Serviço": st.column_config.SelectboxColumn("Item/Serviço", options=list(set(lista_itens)))})
    
    total_orc = (edit_orc['Qtd'] * edit_orc['V. Unit']).sum()
    pgto = st.selectbox("Pagamento", ["PIX", "Dinheiro", "Cartão", "Boleto"])

    c_p1, c_p2 = st.columns(2)
    if c_p1.checkbox("🔍 Ver Pré-visualização Profissional"):
        st.markdown(f"""<div style="border:2px solid #333;padding:30px;background:white;color:black;border-radius:10px">
        <div style="display:flex;justify-content:space-between">
            <div><h2 style="margin:0">{nome_empresa}</h2><small>CNPJ: {format_cnpj(cnpj_i)}</small></div>
            <div style="text-align:right"><b>ORÇAMENTO</b><br>{datetime.now().strftime('%d/%m/%Y')}</div>
        </div><hr>
        <p><b>CLIENTE:</b> {cliente_sel} | <b>TOTAL:</b> R$ {total_orc:,.2f}</p>
        <p style="text-align:center;margin-top:50px">_______________________________________________<br>ASSINATURA DO CLIENTE</p></div>""", unsafe_allow_html=True)

    if c_p2.button("🚀 Gerar e Baixar PDF Oficial"):
        pdf_bytes = gerar_pdf_pro({'nome': nome_empresa, 'cnpj': cnpj_i, 'tel': tel_i, 'end': end_i}, cliente_sel, edit_orc, total_orc, pgto, {'ent': d_ent.strftime('%d/%m/%Y'), 'sai': d_sai.strftime('%d/%m/%Y')}, logo_img)
        st.download_button("📥 Clique aqui para baixar", data=pdf_bytes, file_name=f"Orcamento_{cliente_sel}.pdf", mime="application/pdf")

with tabs[2]: # ABA MEDIDAS/PNEUS
    st.subheader("🛞 Registro de Medidas e Quantidades")
    st.session_state.db_medidas = st.data_editor(st.session_state.db_medidas, num_rows="dynamic", use_container_width=True, key="ed_medidas")

with tabs[6]: # BLOCO DE NOTAS
    st.subheader("📝 Bloco de Notas e Lembretes")
    st.session_state.notas = st.text_area("Escreva aqui informações importantes...", value=st.session_state.notas, height=300)
    st.info("As notas são mantidas enquanto o app estiver aberto.")

# Manutenção das outras abas para não quebrar o sistema
with tabs[1]: st.data_editor(pd.DataFrame([{"OS": "", "Etapa": "Inspeção"}]), num_rows="dynamic", use_container_width=True)
with tabs[3]: st.session_state.db_financeiro = st.data_editor(st.session_state.db_financeiro, num_rows="dynamic", use_container_width=True)
with tabs[4]: st.session_state.db_estoque = st.data_editor(st.session_state.db_estoque, num_rows="dynamic", use_container_width=True)
with tabs[5]: st.session_state.db_clientes = st.data_editor(st.session_state.db_clientes, num_rows="dynamic", use_container_width=True)











import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# 1. CONFIGURAÇÃO E ESTILO ROBUSTO
st.set_page_config(page_title="VULCAT PNEUS - PRO", layout="wide", page_icon="🛞")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    [data-testid="stMetricValue"] { color: #1E3A8A; font-weight: 800; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; padding: 12px 25px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE APOIO
def formatar_cnpj(val):
    val = ''.join(filter(str.isdigit, val))
    if len(val) == 14: return f"{val[:2]}.{val[2:5]}.{val[5:8]}/{val[8:12]}-{val[12:]}"
    return val

def formatar_tel(val):
    val = ''.join(filter(str.isdigit, val))
    if len(val) == 11: return f"({val[:2]}) {val[2:7]}-{val[7:]}"
    return val

# 3. SIDEBAR (LOGOTIPO E DADOS DA EMPRESA)
with st.sidebar:
    st.title("🚜 CONFIGURAÇÃO")
    
    # Upload de Logo direto do computador
    logo_file = st.file_uploader("Subir Logotipo da Empresa", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    nome_empresa = st.text_input("Nome da Empresa", "VULCAT PNEUS")
    cnpj_raw = st.text_input("CNPJ (Apenas números)")
    cnpj_formatado = formatar_cnpj(cnpj_raw)
    
    tel_raw = st.text_input("WhatsApp (Apenas números)")
    tel_formatado = formatar_tel(tel_raw)
    
    endereco = st.text_area("Endereço Completo", "Rua Industrial, 500")
    st.divider()
    st.caption("Vulcat Pneus v5.0 - Gestão Total")

# 4. PAINEL GERAL (DASHBOARD COM GRÁFICOS PIZZA)
st.title(f"📊 PAINEL GERAL - {nome_empresa}")

with st.expander("👁️ VISÃO ESTRATÉGICA (Clique para Minimizar)", expanded=True):
    # Métricas de Topo
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Faturamento Total", "R$ 0,00")
    m2.metric("Despesas (Consumo)", "R$ 0,00", delta_color="inverse")
    m3.metric("Saldo Líquido", "R$ 0,00")
    m4.metric("Serviços em Aberto", "0")

    st.divider()
    
    # Gráficos em modelo Pizza (Pie)
    g1, g2 = st.columns(2)
    
    # Simulação de dados para o gráfico (serão dinâmicos com o banco de dados)
    df_pizza_servicos = pd.DataFrame({"Serviço": ["Recapagem", "Conserto", "Venda"], "Qtd": [0, 0, 0]})
    fig_pizza = px.pie(df_pizza_servicos, values='Qtd', names='Serviço', title="Distribuição de Serviços",
                     hole=.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    g1.plotly_chart(fig_pizza, use_container_width=True)

    df_pizza_estoque = pd.DataFrame({"Item": ["Pneus", "Insumos", "Câmaras"], "Valor": [0, 0, 0]})
    fig_estoque = px.pie(df_pizza_estoque, values='Valor', names='Item', title="Valor em Estoque",
                       hole=.4, color_discrete_sequence=px.colors.qualitative.Safe)
    g2.plotly_chart(fig_estoque, use_container_width=True)

# 5. NAVEGAÇÃO PRINCIPAL (ABAS)
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "🛞 Catálogo Pneus", "💰 Financeiro", "📦 Estoque", "👥 Clientes"])

# --- ABA ORÇAMENTO (COM PDF E ASSINATURA) ---
with tabs[0]:
    st.subheader("📝 Gerar Novo Orçamento Formal")
    
    # Cabeçalho do Orçamento que aparece na tela
    col_logo, col_info = st.columns([1, 3])
    if logo_file: col_logo.image(logo_file, width=150)
    col_info.write(f"**{nome_empresa}** | CNPJ: {cnpj_formatado}")
    col_info.write(f"Tel: {tel_formatado} | {endereco}")

    st.divider()
    c1, c2, c3 = st.columns(3)
    cliente_nome = c1.text_input("Nome do Cliente", key="cli")
    d_ent = c2.date_input("Data de Entrada", key="dent")
    d_sai = c3.date_input("Previsão de Saída", key="dsai")
    
    df_orc = pd.DataFrame([{"Item/Medida": "", "Serviço": "", "Qtd": 1, "V. Unit.": 0.0}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True, key="ed_orc")
    
    total = (edit_orc["Qtd"] * edit_orc["V. Unit."]).sum()
    
    st.write(f"### VALOR TOTAL: R$ {total:,.2f}")
    pagto = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Boleto", "Cartão de Crédito"])
    
    if st.button("🖨️ Gerar Orçamento para Impressão"):
        st.info("Layout de impressão gerado. Use Ctrl+P para salvar em PDF.")
        st.write("---")
        st.write("__________________________________________")
        st.write(f"Assinatura do Cliente: {cliente_nome}")

# --- ABA PRODUÇÃO (FICHA SEM VALOR) ---
with tabs[1]:
    st.subheader("🛠️ Ficha de Produção (Oficina)")
    df_prod = pd.DataFrame([{"OS": "", "Série Pneu": "", "Serviço": "", "Etapa": "Inspeção", "Status": "Pendente"}])
    st.data_editor(df_prod, num_rows="dynamic", use_container_width=True)

# --- ABA CATÁLOGO DE PNEUS ---
with tabs[2]:
    st.subheader("🛞 Cadastro de Medidas e Valores Base")
    df_medidas = pd.DataFrame([{"Medida": "", "Aplicação": "", "Preço Base": 0.0}])
    st.data_editor(df_medidas, num_rows="dynamic", use_container_width=True)

# --- ABA FINANCEIRO (ENTRADAS E SAÍDAS ZERADAS) ---
with tabs[3]:
    st.subheader("💰 Livro de Caixa (Entradas e Saídas)")
    st.write("Registre aqui todos os consumos e ganhos da empresa.")
    
    df_fin = pd.DataFrame([{"Data": datetime.now().date(), "Tipo": "Entrada", "Descrição": "", "Valor": 0.0}])
    edit_fin = st.data_editor(df_fin, num_rows="dynamic", use_container_width=True, key="ed_fin")
    
    ent = edit_fin[edit_fin["Tipo"] == "Entrada"]["Valor"].sum()
    sai = edit_fin[edit_fin["Tipo"] == "Saída"]["Valor"].sum()
    
    c_ent, c_sai, c_sal = st.columns(3)
    c_ent.metric("Total de Entradas", f"R$ {ent:,.2f}")
    c_sai.metric("Total de Saídas (Consumo)", f"R$ {sai:,.2f}", delta_color="inverse")
    c_sal.metric("Resultado Líquido", f"R$ {(ent-sai):,.2f}")

# --- ABA ESTOQUE ---
with tabs[4]:
    st.subheader("📦 Controle de Estoque")
    df_est = pd.DataFrame([{"Item": "", "Quantidade": 0, "Mínimo Alerta": 5}])
    st.data_editor(df_est, num_rows="dynamic", use_container_width=True)

# --- ABA CLIENTES ---
with tabs[5]:
    st.subheader("👥 Cadastro de Clientes")
    df_cli = pd.DataFrame([{"Nome/Empresa": "", "CNPJ/CPF": "", "Telefone": "", "Cidade": ""}])
    st.data_editor(df_cli, num_rows="dynamic", use_container_width=True)













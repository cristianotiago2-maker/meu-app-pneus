import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# 1. CONFIGURAÇÃO E MEMÓRIA
st.set_page_config(page_title="VULCAT PNEUS - SISTEMA GESTÃO", layout="wide", page_icon="🛞")

if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = pd.DataFrame(columns=["Nome", "CPF/CNPJ", "Telefone", "Endereço", "Cidade"])
if 'db_estoque' not in st.session_state:
    st.session_state.db_estoque = pd.DataFrame([{"Item": "Recapagem 295/80", "Qtd": 10}, {"Item": "Conserto Vulcanização", "Qtd": 100}])
if 'db_financeiro' not in st.session_state:
    st.session_state.db_financeiro = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])

# 2. FUNÇÕES DE APOIO
def format_cnpj(v):
    v = ''.join(filter(str.isdigit, v))
    if len(v) == 14: return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    return v

def format_tel(v):
    v = ''.join(filter(str.isdigit, v))
    if len(v) == 11: return f"({v[:2]}) {v[2:7]}-{v[7:]}"
    return v

# 3. SIDEBAR
with st.sidebar:
    st.title("⚙️ CONFIGURAÇÕES")
    logo_file = st.file_uploader("Carregar Logotipo (PC)", type=['png', 'jpg', 'jpeg'])
    nome_empresa = st.text_input("Nome da Empresa", "VULCAT PNEUS")
    cnpj_input = st.text_input("CNPJ (números)")
    tel_empresa = st.text_input("Telefone (números)")
    endereco_empresa = st.text_area("Endereço Completo")
    st.divider()
    st.caption("v7.0 PRO com Pré-Visualização")

# 4. PAINEL GERAL (DASHBOARD)
st.title(f"🚜 {nome_empresa}")
with st.expander("📈 PAINEL GERAL E INDICADORES", expanded=True):
    ent = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Entrada"]['Valor'].sum()
    sai = st.session_state.db_financeiro[st.session_state.db_financeiro['Tipo'] == "Saída"]['Valor'].sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento", f"R$ {ent:,.2f}")
    c2.metric("Consumo/Saídas", f"R$ {sai:,.2f}", delta_color="inverse")
    c3.metric("Saldo", f"R$ {(ent-sai):,.2f}")
    c4.metric("Itens Estoque", st.session_state.db_estoque['Qtd'].sum() if not st.session_state.db_estoque.empty else 0)

# 5. ABAS
tabs = st.tabs(["📄 Orçamento", "🛠️ Produção", "💰 Financeiro", "📦 Estoque", "👥 Clientes"])

# --- ABA ORÇAMENTO COM PRÉ-VISUALIZAÇÃO ---
with tabs[0]:
    st.subheader("📝 Montar Orçamento")
    
    o1, o2 = st.columns(2)
    lista_nomes = st.session_state.db_clientes['Nome'].tolist()
    cliente_sel = o1.selectbox("Selecionar Cliente", [""] + lista_nomes)
    d_ent = o2.date_input("Data de Entrada", format="DD/MM/YYYY")
    d_sai = o2.date_input("Previsão de Saída", format="DD/MM/YYYY")

    lista_itens_estoque = st.session_state.db_estoque['Item'].tolist()
    df_orc = pd.DataFrame([{"Item/Serviço": "", "Qtd": 1, "V. Unit": 0.0}])
    edit_orc = st.data_editor(df_orc, num_rows="dynamic", use_container_width=True, key="ed_orc",
                             column_config={"Item/Serviço": st.column_config.SelectboxColumn("Item/Serviço", options=lista_itens_estoque)})
    
    total_orc = (edit_orc['Qtd'] * edit_orc['V. Unit']).sum()
    pgto = st.selectbox("Forma de Pagamento", ["PIX", "Dinheiro", "Boleto", "Cartão"])

    st.divider()
    
    # --- LÓGICA DE PRÉ-VISUALIZAÇÃO ---
    if st.checkbox("🔍 ATIVAR PRÉ-VISUALIZAÇÃO DO ORÇAMENTO"):
        st.markdown(f"""
        <div style="border: 2px solid #ccc; padding: 30px; background-color: white; color: black; border-radius: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 24px; font-weight: bold;">{nome_empresa.upper()}</div>
                <div style="text-align: right; font-size: 12px;">
                    CNPJ: {format_cnpj(cnpj_input)} <br> Tel: {format_tel(tel_empresa)} <br> {endereco_empresa}
                </div>
            </div>
            <hr>
            <div style="margin: 20px 0;">
                <strong>CLIENTE:</strong> {cliente_sel} <br>
                <strong>DATA ENTRADA:</strong> {d_ent.strftime('%d/%m/%Y')} | <strong>PREVISÃO SAÍDA:</strong> {d_sai.strftime('%d/%m/%Y')}
            </div>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 8px;">Item/Serviço</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">Qtd</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">V. Unit</th>
                </tr>
                {"".join([f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{row['Item/Serviço']}</td><td style='border: 1px solid #ddd; padding: 8px;'>{row['Qtd']}</td><td style='border: 1px solid #ddd; padding: 8px;'>R$ {row['V. Unit']:,.2f}</td></tr>" for _, row in edit_orc.iterrows()])}
            </table>
            <div style="text-align: right; font-size: 18px; font-weight: bold; margin-top: 10px;">
                TOTAL: R$ {total_orc:,.2f}
            </div>
            <div style="margin-top: 10px;"><strong>Forma de Pagamento:</strong> {pgto}</div>
            <div style="margin-top: 50px; border-top: 1px solid black; width: 300px; margin-left: auto; margin-right: auto; text-align: center;">
                Assinatura do Cliente
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("\n")
        st.info("✅ Se as informações acima estiverem corretas, use **Ctrl + P** no teclado para imprimir ou salvar em PDF.")

# --- OUTRAS ABAS (MANUTENÇÃO DA COMUNICAÇÃO) ---
with tabs[1]: # Produção
    st.subheader("🛠️ Ficha de Oficina")
    st.data_editor(pd.DataFrame([{"Série": "", "Serviço": "", "Etapa": "Inspeção", "Status": "Pendente"}]), num_rows="dynamic", use_container_width=True)

with tabs[2]: # Financeiro
    st.subheader("💰 Fluxo de Caixa")
    st.session_state.db_financeiro = st.data_editor(st.session_state.db_financeiro, num_rows="dynamic", use_container_width=True, column_config={
        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Entrada", "Saída"])
    })

with tabs[3]: # Estoque
    st.subheader("📦 Gestão de Estoque")
    st.session_state.db_estoque = st.data_editor(st.session_state.db_estoque, num_rows="dynamic", use_container_width=True)

with tabs[4]: # Clientes
    st.subheader("👥 Cadastro de Clientes")
    st.session_state.db_clientes = st.data_editor(st.session_state.db_clientes, num_rows="dynamic", use_container_width=True)












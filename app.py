import streamlit as st
import json, os
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

DB = "db.json"

# ===== BANCO =====
if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump({
            "usuarios":[{"login":"admin","senha":"123"}],
            "clientes":[],
            "producoes":[],
            "estoque":[],
            "financeiro":[]
        }, f)

def read_db():
    return json.load(open(DB))

def save_db(data):
    json.dump(data, open(DB,"w"), indent=2)

# ===== LOGIN =====
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login Vulcat")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        db = read_db()
        ok = any(u["login"]==user and u["senha"]==senha for u in db["usuarios"])
        if ok:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Login inválido")

    st.stop()

# ===== MENU =====
st.set_page_config(layout="wide")
st.title("🏆 Vulcat Sistema Profissional")

menu = st.sidebar.selectbox("Menu", [
    "Dashboard","Clientes","Produção","Estoque","Financeiro"
])

db = read_db()

# ===== DASHBOARD =====
if menu == "Dashboard":
    st.subheader("📊 Visão Geral")

    total = sum(f["valor"] for f in db["financeiro"]) if db["financeiro"] else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Clientes", len(db["clientes"]))
    c2.metric("Produções", len(db["producoes"]))
    c3.metric("Itens Estoque", len(db["estoque"]))
    c4.metric("Faturamento", f"R$ {total}")

# ===== CLIENTES =====
elif menu == "Clientes":
    st.subheader("👥 Cadastro")

    nome = st.text_input("Nome")
    tel = st.text_input("Telefone")

    if st.button("Salvar Cliente"):
        db["clientes"].append({
            "id": len(db["clientes"])+1,
            "nome": nome,
            "tel": tel
        })
        save_db(db)
        st.success("Salvo!")

    st.dataframe(pd.DataFrame(db["clientes"]))

# ===== PRODUÇÃO =====
elif menu == "Produção":
    st.subheader("🔧 Nova Produção")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")
    pneu = st.text_input("Pneu")
    valor = st.number_input("Valor", 0.0)

    if st.button("Salvar Produção"):
        p = {
            "id": len(db["producoes"])+1,
            "cliente": cliente,
            "servico": servico,
            "pneu": pneu,
            "valor": valor
        }
        db["producoes"].append(p)

        db["financeiro"].append({"valor": valor})

        save_db(db)
        st.success("Produção salva!")

    st.divider()

    st.subheader("📋 Lista")

    for p in db["producoes"]:
        col1, col2 = st.columns([4,1])

        col1.write(f"{p['cliente']} | {p['servico']} | {p['pneu']}")

        if col2.button("PDF", key=p["id"]):
            file = f"ficha_{p['id']}.pdf"

            doc = SimpleDocTemplate(file)
            styles = getSampleStyleSheet()

            content = [
                Paragraph("VULCAT PNEUS", styles["Title"]),
                Paragraph(f"Cliente: {p['cliente']}", styles["Normal"]),
                Paragraph(f"Serviço: {p['servico']}", styles["Normal"]),
                Paragraph(f"Pneu: {p['pneu']}", styles["Normal"]),
                Paragraph("SEM VALORES", styles["Normal"])
            ]

            doc.build(content)

            with open(file, "rb") as f:
                st.download_button("Baixar PDF", f, file_name=file)

# ===== ESTOQUE =====
elif menu == "Estoque":
    st.subheader("📦 Controle")

    nome = st.text_input("Item")
    qtd = st.number_input("Quantidade", 0)
    min = st.number_input("Mínimo", 1, value=5)

    if st.button("Salvar Item"):
        db["estoque"].append({
            "nome": nome,
            "qtd": qtd,
            "min": min
        })
        save_db(db)

    st.divider()

    for i in db["estoque"]:
        if i["qtd"] <= i["min"]:
            st.warning(f"⚠️ {i['nome']} baixo ({i['qtd']})")
        else:
            st.success(f"{i['nome']} OK ({i['qtd']})")

# ===== FINANCEIRO =====
elif menu == "Financeiro":
    st.subheader("💰 Controle")

    total = sum(f["valor"] for f in db["financeiro"]) if db["financeiro"] else 0

    st.metric("Total", f"R$ {total}")

    st.dataframe(pd.DataFrame(db["financeiro"]))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import io
import streamlit_authenticator as stauth

# ✅ Definir configuração da página como primeiro comando Streamlit
st.set_page_config(page_title="Sistema de Assinaturas", page_icon="📋")

# ========== AUTENTICAÇÃO ==========
# Hash de senhas seguras para os usuários (geradas em lote)
hashes = stauth.Hasher([
    "1234",
    "adminpass",
    "basedeclientes2025"
]).generate()

usuarios = {
    "jhow": hashes[0],
    "admin": hashes[1],
    "weslley.amorim": hashes[2]
}

authenticator = stauth.Authenticate(
    {"usernames": {
        "jhow": {"name": "Jonathan", "password": usuarios["jhow"]},
        "admin": {"name": "Administrador", "password": usuarios["admin"]},
        "weslley.amorim": {"name": "Weslley Amorim", "password": usuarios["weslley.amorim"]}
    }},
    "baseclientes_app",  # ID do cookie
    "abcdef",            # Segredo do cookie
    cookie_expiry_days=1
)

# Login
nome, autenticado, nome_usuario = authenticator.login("Login", "main")

# Botão de logout
authenticator.logout("Sair", "sidebar")

if not autenticado:
    st.stop()

# ===================================

# 📁 Caminho do arquivo Excel
arquivo_excel = "clientes.xlsx"

# 📅 Carregar dados
def carregar_dados():
    if os.path.exists(arquivo_excel):
        return pd.read_excel(arquivo_excel)
    else:
        return pd.DataFrame(columns=["Nome", "Telefone", "Serviço", "Valor", "Data de Início", "Próximo Pagamento", "Status"])

# 📆 Salvar dados
def salvar_dados(df):
    df.to_excel(arquivo_excel, index=False)

# 🔄 Atualizar status automático
def atualizar_status(df):
    hoje = datetime.today().date()
    for i, row in df.iterrows():
        try:
            data_pagamento = pd.to_datetime(row["Próximo Pagamento"]).date()
            if data_pagamento < hoje:
                df.at[i, "Status"] = "Atrasado"
            else:
                df.at[i, "Status"] = "Em dia"
        except:
            df.at[i, "Status"] = "Desconhecido"
    return df

# 🌟 Layout
st.title("📋 Sistema de Assinaturas")

aba = st.sidebar.selectbox("Escolha uma opção", ["📅 Cadastrar Cliente", "📊 Ver Clientes"])

df_clientes = carregar_dados()
df_clientes = atualizar_status(df_clientes)

# ✅ ABA: Cadastro
if aba == "📅 Cadastrar Cliente":
    st.header("Cadastrar novo cliente")

    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    servico = st.text_input("Serviço")
    valor = st.number_input("Valor da assinatura (R$)", min_value=0.0, step=10.0)
    data_inicio = st.date_input("Data de início", value=datetime.today())
    dias_renovacao = st.number_input("Dias para próximo pagamento", value=30)

    if st.button("Salvar Cliente"):
        proximo_pagamento = data_inicio + timedelta(days=int(dias_renovacao))
        novo = pd.DataFrame([[nome, telefone, servico, valor, data_inicio, proximo_pagamento, "Em dia"]],
                            columns=df_clientes.columns)
        df_clientes = pd.concat([df_clientes, novo], ignore_index=True)
        salvar_dados(df_clientes)
        st.success("✅ Cliente salvo com sucesso!")

# ✅ ABA: Ver Clientes
elif aba == "📊 Ver Clientes":
    st.header("Lista de clientes")

    filtro = st.selectbox("Filtrar por status", ["Todos", "Em dia", "Atrasado"])
    if filtro != "Todos":
        df_mostrar = df_clientes[df_clientes["Status"] == filtro]
    else:
        df_mostrar = df_clientes

    st.dataframe(df_mostrar)

    # 📄 Exportar Excel
    st.subheader("📅 Exportar dados em Excel")

    buffer = io.BytesIO()
    df_mostrar.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📄 Baixar Excel",
        data=buffer,
        file_name="clientes_exportados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 💳 Registrar pagamento
    st.subheader("Registrar pagamento de cliente")
    if not df_clientes.empty:
        nome_pagamento = st.selectbox("Escolha o cliente", df_clientes["Nome"].unique(), key="pagamento")
        if st.button("Registrar pagamento"):
            idx = df_clientes[df_clientes["Nome"] == nome_pagamento].index[0]
            nova_data = datetime.today() + timedelta(days=30)
            df_clientes.at[idx, "Próximo Pagamento"] = nova_data
            df_clientes.at[idx, "Status"] = "Em dia"
            salvar_dados(df_clientes)
            st.success(f"✅ Pagamento registrado para {nome_pagamento}!")

    # 🔑 Remover cliente
    st.subheader("Remover cliente da base")
    if not df_clientes.empty:
        nome_remover = st.selectbox("Selecione o cliente para remover", df_clientes["Nome"].unique(), key="remover")
        if st.button("Remover cliente"):
            df_clientes = df_clientes[df_clientes["Nome"] != nome_remover]
            salvar_dados(df_clientes)
            st.success(f"🔑 Cliente '{nome_remover}' removido com sucesso!")

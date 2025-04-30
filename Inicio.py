import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Caminho do Excel
arquivo_excel = 'registro_ranking.xlsx'

# Lista de usuários (login: senha)
usuarios = {
    "diana.barbosa": "Verisure",
    "joao.goncalves": "Verisure",
    "laryssa.klein": "Verisure",
    "weslley.amorim": "Verisure",
    "isabelly.costa": "Verisure",
    "dianne.goncalves": "Verisure",
    "sara.souza": "Verisure",
    "julia.gomes": "Verisure",
    "dayse.santos": "Verisure",
    "davi.guerra": "Verisure",
    "maria.espirito": "Verisure",
    "caroline.silva": "Verisure",
    "jonathan.miranda": "Verisure",
    "gabriel.rossi": "Verisure"
}

# Lista de supervisores com permissão de exclusão e download
supervisores = ["jonathan.miranda", "gabriel.rossi"]

# Sessão
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# Tela de login
def login():
    st.title("Login - BackOffice")
    nome = st.text_input("Login (ex: nome.sobrenome)")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if nome in usuarios and usuarios[nome] == senha:
            st.session_state.usuario_logado = nome
            st.success(f"Bem-vindo, {nome}!")
            st.rerun()
        else:
            st.error("Login ou senha inválidos.")

# Tela principal
def app():
    st.title("Registro para Ranking - BackOffice")
    st.write(f"Usuário logado: **{st.session_state.usuario_logado}**")

    if st.button("Sair"):
        st.session_state.usuario_logado = None
        st.rerun()

    # Criar Excel se não existir
    if not os.path.exists(arquivo_excel):
        df_vazio = pd.DataFrame(columns=['Data/Hora', 'Assistente', 'RE', 'Foi associada para o ranking?'])
        df_vazio.to_excel(arquivo_excel, index=False)

    re_input = st.text_input("Digite o número RE")
    resposta = st.radio("Foi associada para o ranking?", ["Sim", "Não"])

    if st.button("Salvar"):
        if re_input.strip() == "":
            st.warning("Por favor, digite um número RE.")
        else:
            df_existente = pd.read_excel(arquivo_excel)
            novo_dado = pd.DataFrame({
                'Data/Hora': [datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
                'Assistente': [st.session_state.usuario_logado],
                'RE': [re_input],
                'Foi associada para o ranking?': [resposta]
            })
            df_atualizado = pd.concat([df_existente, novo_dado], ignore_index=True)
            df_atualizado.to_excel(arquivo_excel, index=False)
            st.success("Registro salvo com sucesso!")
            st.rerun()

    st.subheader("Registros Salvos")
    df_visualizacao = pd.read_excel(arquivo_excel)

    if st.session_state.usuario_logado in supervisores:
        st.write("🔒 Supervisão: Você pode apagar registros abaixo.")
        df_visualizacao['Selecionar'] = False

        for i in df_visualizacao.index:
            item = f"{df_visualizacao.at[i, 'RE']} - {df_visualizacao.at[i, 'Assistente']}"
            df_visualizacao.at[i, 'Selecionar'] = st.checkbox(item, key=f"ck_{i}")

        if st.button("Apagar selecionados"):
            df_filtrado = df_visualizacao[df_visualizacao['Selecionar'] == False]
            df_filtrado = df_filtrado.drop(columns=['Selecionar'])
            df_filtrado.to_excel(arquivo_excel, index=False)
            st.success("Registros selecionados foram apagados.")
            st.rerun()

        st.write("Registros atuais:")
        st.dataframe(df_visualizacao.drop(columns=['Selecionar']))

        # Botão de download
        with open(arquivo_excel, "rb") as f:
            conteudo = f.read()
            st.download_button(
                label="📥 Baixar registros (Excel)",
                data=conteudo,
                file_name="registro_ranking.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.info("Você não tem permissão para apagar registros.")
        st.dataframe(df_visualizacao)

# Roteamento
if st.session_state.usuario_logado:
    app()
else:
    login()



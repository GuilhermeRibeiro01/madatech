import streamlit as st
import requests
import base64
import os
from sys import argv
from re import match, IGNORECASE
import json
import re

PAGE_SELECTION_KEY = "page_selection"
ENDPOINT_URL = "https://ikq8cj1uae.execute-api.us-east-1.amazonaws.com"

selected_archives = []

if PAGE_SELECTION_KEY not in st.session_state:
    st.session_state[PAGE_SELECTION_KEY] = "Adicione Empresa"

create_company_page = st.sidebar.button("Adicione Empresa")
# update_company_page = st.sidebar.button("Atualize Empresa")
company_page = st.sidebar.button("Empresas")
chat_page = st.sidebar.button("Chat")
signed_url_page = st.sidebar.button("Upload de documento")
delete_company = st.sidebar.button("Deletar Empresa")

if create_company_page:
    st.session_state[PAGE_SELECTION_KEY] = "Adicione Empresa"
elif company_page:
    st.session_state[PAGE_SELECTION_KEY] = "Empresas"
elif chat_page:
    st.session_state[PAGE_SELECTION_KEY] = "Chat"
# elif update_company_page:
#     st.session_state[PAGE_SELECTION_KEY] = "Atualize Empresa"
elif signed_url_page:
    st.session_state[PAGE_SELECTION_KEY] = "Upload de documento"
elif delete_company:
    st.session_state[PAGE_SELECTION_KEY] = "Deletar Empresa"

if st.session_state[PAGE_SELECTION_KEY] == "Adicione Empresa":
    st.title("🏢 Adicione Empresa")
    id = st.text_input("Empresa ID")
    company_name = st.text_input("Nome da Empresa")
    prompt = 'aja como um consultor'

    create_company_button = st.button("Adicionar Empresa", key="create_company")

    if create_company_button:
        api_data = {
            "company_id": id,
            "company_name": company_name,
            "prompt": prompt,
        }

        try:
            response = requests.post(ENDPOINT_URL + "/company", json=api_data)
            if response.status_code == 200:
                st.success(f"Empresa '{company_name}' criada com sucesso!")
            else:
                st.error("Falha ao criar a empresa. Por favor, tente novamente.")
        except Exception as e:
            st.error(f"Um erro ocorreu: {str(e)}")

elif st.session_state[PAGE_SELECTION_KEY] == "Atualize Empresa":
    st.title("🔄 Atualize Empresa")

    try:
        response = requests.get(ENDPOINT_URL + "/company")
        if response.status_code == 200:
            companies = response.json()
            company_id_options = [company["name"] for company in companies]
        else:
            st.error("Falha ao obter a lista de empresas. Por favor, tente novamente.")
            st.stop()
    except Exception as e:
        st.error(f"Um erro ocorreu: {str(e)}")
        st.stop()

    selected_company_name = st.selectbox("Selecione a Empresa", company_id_options)

    selected_company_id = next(
        (company['id'] for company in companies if company["name"] == selected_company_name),
        None,
    )


    option = st.radio("Escolha entre passar um documento ou uma lista de URLs", ("Documento", "Links"))

    if option == "Documento":
        document_type = st.selectbox("Tipo de Documento", ["pdf"])
        product_id = st.selectbox("Tipo de seguro", ["Vida", "Automóvel"])
        document_file = st.file_uploader("Upload", type=["pdf"])


        update_company_button = st.button("Atualizar Empresa", key="update_company")

        if update_company_button and document_file:
            base64_content = base64.b64encode(document_file.getvalue()).decode()

            api_data = {
                "id": selected_company_id,
                "product_id": product_id,
                "documentType": document_type,
                "documentContent": base64_content,
            }

            try:
                response = requests.patch(ENDPOINT_URL + "/company", json=api_data)
                print(response)
                if response.status_code == 200:
                    st.success(f"Empresa '{selected_company_name}' atualizada com sucesso!")
                else:
                    st.error("Falha ao atualizar a empresa. Por favor, tente novamente.")
            except Exception as e:
                st.error(f"Um erro ocorreu: {str(e)}")

    elif option == "Links":
        st.subheader("Lista de URLs")
        urls = st.text_input("Novo item")

        if "lista" not in st.session_state:
            st.session_state["lista"] = []

        if st.button('Adicionar'):
            if urls:
                st.session_state.lista.append(urls)

        if st.session_state.lista:
            lista_str = "\n".join(st.session_state.lista)
            st.text_area("Itens da Lista", value=lista_str, height=200)

        update_company_button = st.button("Atualizar Empresa", key="update_company")

        if update_company_button and st.session_state.lista:

            api_data = {
                "company_id": selected_company_id,
                "prompt": prompt,
                "urls": st.session_state.lista
            }

            try:
                response = requests.post(ENDPOINT_URL + "/company", json=api_data)
                if response.status_code == 200:
                    st.success(f"Empresa '{selected_company_name}' atualizada com sucesso!")
                else:
                    st.error("Falha ao atualizar a empresa. Por favor, tente novamente.")
            except Exception as e:
                st.error(f"Um erro ocorreu: {str(e)}")

if st.session_state[PAGE_SELECTION_KEY] == "Empresas":
    st.title("🏢 Empresas")

    try:
        response = requests.get(ENDPOINT_URL + "/company")
        if response.status_code == 200:
            data = response.json()
        else:
            st.error("Falha ao trazer empresas. Por favor, tente novamente.")
    except Exception as e:
        st.error(f"Um erro ocorreu: {str(e)}")

    if 'data' in locals():
        for i, company in enumerate(data):
            st.text_input(label='Company Name', value=company['name'], disabled=True, key=f"checkbox_{company['name']}-{i}")

            company_id = company['id']

            # Verificar se o campo 'sync' existe e é False
            if 'sync' in company and company['sync'] == False:
                st.warning("Esta empresa ainda não foi sincronizada.")

            # try:
            #     response = requests.get(ENDPOINT_URL + f"/company/{company_id}")
            #     if response.status_code == 200:
            #         items = response.json()
            #     else:
            #         st.error("Falha ao trazer arquivos. Por favor, tente novamente.")
            # except Exception as e:
            #     st.error(f"Um erro ocorreu: {str(e)}")

            items = company['archives']

            if items is not None and items:
                for i, archive in enumerate(company['archives']):
                    checkbox_selected = st.checkbox(f"🔗 {archive['archive_name']}", key=f"checkbox_{company_id}_{archive['archive_name']}-{i}")
                    if checkbox_selected:
                        selected_archives.append(archive['archive_name'])

                delete_path = st.button("Excluir", key=f"delete_{company_id}_{i}")

                if delete_path:
                    body = {
                        "paths": selected_archives
                    }
                    
                    try:
                        response = requests.post(ENDPOINT_URL + f"/company/{company_id}/delete", json=body)
                        if response.status_code == 200:
                            st.success(f"Arquivo excluído com sucesso!")
                        else:
                            st.error("Falha ao excluir os arquivos. Por favor, tente novamente.")
                    except Exception as e:
                        st.error(f"Um erro ocorreu: {str(e)}")
elif st.session_state[PAGE_SELECTION_KEY] == "Chat":
    st.title("💬 Chatbot")

    try:
        response = requests.get(ENDPOINT_URL + "/company")
        if response.status_code == 200:
            companies = response.json()
            print('companies', companies)
            company_id_options = [company["name"] for company in companies]
        else:
            st.error("Falha ao obter a lista de empresas. Por favor, tente novamente.")
            st.stop()
    except Exception as e:
        st.error(f"Um erro ocorreu: {str(e)}")
        st.stop()

    # selected_company_name = st.selectbox("Empresa", company_id_options)

    company_name = st.text_input("Nome da Empresa")

    # selected_company_id = next(
    #     (company['id'] for company in companies if company["name"] == selected_company_name),
    #     None,
    # )

    # print('selected_company_id', selected_company_id)
    products = {
        "AUTO": "AUTO",
    }

    products_options = list(products.keys())

    product_id = st.selectbox("Modelo", products_options)

    models = {
        "claude-v3-haiku":"anthropic.claude-3-haiku-20240307-v1:0",
        "claude-v3-5-sonnet":"anthropic.claude-3-5-sonnet-20240620-v1:0",
        "claude-v3-5-sonnet-v2":"us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "claude-v3-5-haiku":"us.anthropic.claude-3-5-haiku-20241022-v1:0",
    }

    model_id_options = list(models.keys())

    selected_model_id = st.selectbox("Modelo", model_id_options)
    # show_citations = st.checkbox("Mostrar citações")

    chosen_company_id = company_name
    chosen_model_id = models[selected_model_id]

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Como posso ajudar você?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        request_data = {
            "question": prompt,
            "companyId": chosen_company_id,
            "productId": product_id,
            "modelId": chosen_model_id,
        }

        headers = {"content-type": "application/json"}

        print('request_data', request_data)

        lambda_url = 'https://vkyh7mduinmkpnwvtlwx5opqfe0hfach.lambda-url.us-east-1.on.aws/chat'

        response_container = st.empty()

        def fetch_bot_response():
            document_citation = False
            try:
                response = requests.post(lambda_url, json=request_data, headers=headers, stream=True, timeout=60)
                print("RESPONSE STATUS:", response.status_code)

                if response.status_code == 200:
                    bot_response = ""  # String acumuladora para todos os chunks da resposta
                    st.session_state.messages.append({"role": "assistant", "content": ""})
                    message_placeholder = response_container  # Usando `response_container` para atualização contínua
                    citations = []
                    unique_documents = []
                    for chunk in response.iter_content(chunk_size=2000):
                        if chunk:
                            data = chunk.decode()
                            print(data)
                            try:
                                # json_data = json.loads(data)
                                
                                new_content = data
                                bot_response += new_content

                                message_placeholder.markdown(f"<p>{bot_response}</p>", unsafe_allow_html=True)
                                st.session_state.messages[-1]["content"] = bot_response

                                # Lista para armazenar os documentos únicos
                                # print("JSON DATA: ",json_data)
                                # if show_citations:
                                #     if document_citation == False:
                                #         if "documents" in json_data:
                                #             for doc in json_data["documents"]:
                                #                 if doc not in unique_documents:
                                #                     citation = doc
                                #                     citations.append(citation)
                                #                     unique_documents.append(doc)
                                #             document_citation = True
                                #         st.markdown(f"**Fontes dos documentos:** {', '.join(citations)}")
                                # Processa as citações APÓS coletar todos os documentos únicos
                                # if show_citations and unique_documents: # Verifica se unique_documents não está vazio
                                    
                                #     for doc in unique_documents:
                                #         citation = doc.get("name", "Nome não disponível") # Lidar com casos onde "name" pode não existir
                                #         citations.append(citation)

                                    # Exibe as citações FORA do loop, após processar todos os documentos
                                # print(citations[0])
                    
                                
                            except json.JSONDecodeError as e:
                                print("Erro ao decodificar JSON:", e)
                                continue
                    # if show_citations:
                    #     for doc in unique_documents:
                    #             citation = doc # Lidar com casos onde "name" pode não existir
                    #             citations.append(citation)  
                        # st.markdown(f"**Fontes dos documentos:** {', '.join(citations)}")
                else:
                    st.error("Falha ao obter uma resposta da API.")
                    st.session_state.messages.append({"role": "assistant", "content": "Falha ao obter uma resposta da API."})

            except Exception as e:
                st.error(f"Ocorreu um erro ao tentar enviar o pedido: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Ocorreu um erro: {e}"})

        # Chama a função para processar a resposta em chunks
        fetch_bot_response()





elif st.session_state[PAGE_SELECTION_KEY] == "Upload de documento":
    st.title("Upload de documento")

    try:
        response = requests.get(ENDPOINT_URL + "/company")
        if response.status_code == 200:
            companies = response.json()
            company_id_options = [company["name"] for company in companies]
        else:
            st.error("Falha ao obter a lista de empresas. Por favor, tente novamente.")
            st.stop()
    except Exception as e:
        st.error(f"Um erro ocorreu: {str(e)}")
        st.stop()

    selected_company_name = st.selectbox("Selecione a Empresa", company_id_options)

    selected_company_id = next(
        (company['id'] for company in companies if company["name"] == selected_company_name),
        None,
    )

    product_id = st.text_input("Tipo de seguro" )
    document_type = st.selectbox("Tipo de Documento", ["pdf"])

    arquivo = st.file_uploader("Escolha um arquivo", type=['pdf'])

    if arquivo:
        nome_arquivo = os.path.basename(arquivo.name)
        st.write("Nome do arquivo:", nome_arquivo)

        if st.button("Enviar"):
            # Dados para a requisição da URL assinada
            dados_requisicao = {
                "object_key": nome_arquivo,  # Adicionar object_key aqui
                "id": selected_company_id, 
                "product_id": product_id,
                "documentType": document_type,
            }

            # 1. Obter URL assinada da API (incluindo metadados na requisição)
            url_assinada_resposta = requests.post(
                ENDPOINT_URL + "/signed-url", json=dados_requisicao 
            )

            if url_assinada_resposta.status_code == 200:
                url_assinada = url_assinada_resposta.json().get("uploadURL")

                upload_resposta = requests.put(url_assinada, data=arquivo)

                if upload_resposta.status_code == 200:
                    st.success("Arquivo enviado com sucesso!")
                else:
                    st.error(f"Erro ao enviar arquivo: {upload_resposta.text}")
            else:
                st.error(f"Erro ao obter URL assinada: {url_assinada_resposta.text}")

elif st.session_state[PAGE_SELECTION_KEY] == "Deletar Empresa":
    st.title("🏢 Delete uma Empresa")
    try:
        response = requests.get(ENDPOINT_URL + "/company")
        if response.status_code == 200:
            companies = response.json()
            company_id_options = [company["name"] for company in companies]
        else:
            st.error("Falha ao obter a lista de empresas. Por favor, tente novamente.")
            st.stop()
    except Exception as e:
        st.error(f"Um erro ocorreu: {str(e)}")
        st.stop()

    selected_company_name = st.selectbox("Selecione a Empresa", company_id_options)

    selected_company_id = next(
        (company['id'] for company in companies if company["name"] == selected_company_name),
        None,
    )
    
    
    def delete_company(company_id):
        """Função para deletar uma empresa pelo ID."""
        response = requests.delete(ENDPOINT_URL + f"/company/delete/{company_id}")
        if response.status_code == 200:
            return st.success("Empresa deletada com sucesso!")
        elif response.status_code == 400:
            return st.error("ID da empresa inválido.")
        elif response.status_code == 404:
            return st.error("Empresa não encontrada.")
        else:
            return "Falha ao deletar a empresa. Por favor, tente novamente."
    
    # Botão para deletar empresa com uma chave única
    if st.button("Deletar Empresa", key="delete_company_button"):
        delete_company(selected_company_id)
            

    

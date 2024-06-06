import os
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
from pdf_handler import handle_pdf_upload

# Ensure environment variables are set
load_dotenv()

# Initialize the Azure OpenAI service
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
client = AzureOpenAI(api_version="2023-03-15-preview")

USER_NAME = "user"
ASSISTANT_NAME = "assistant"
model = "azure_openai_app"

st.title("TB PDF-Chatbot")  # Name of Application
st.write("Please upload your pdf file and type message")
                
def response_chatgpt(user_msg: str, input_documents, chat_history: list = []):
    system_msg = """You are an Assistant. Answer the questions based only on the provided documents. 
                    If the information is not in the documents, say you don't know the answer but user may find something relevant in sources given below."""
    messages = [{"role": "system", "content": system_msg}]

    # If there is a chat log, add it to the messages list
    if len(chat_history) > 0:
        for chat in chat_history:
            messages.append({"role": chat["name"], "content": chat["msg"]})

    # Add user message to messages list
    messages.append({"role": USER_NAME, "content": user_msg})

    # Append input documents to the messages list
    for doc in input_documents:
        messages.append({"role": "user", "content": f"Document snippet:\n{doc['content']}"})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return {
            "answer": response.choices[0].message.content,
            "sources": input_documents
        }
    except Exception as e:
        st.error(f"Could not find llm model: {str(e)}")
        return None


def main():
    # Sidebar for PDF upload
    with st.sidebar:
        st.title('PDF Chat Loader')
        pdf = st.file_uploader("Upload your PDF", accept_multiple_files=False, type='pdf')
        send_button = st.button("Submit", key="send_button")
        if send_button:
            try:
                vectordb = handle_pdf_upload(pdf)
                pdf_name = pdf.name
            except Exception as e:
                st.error(f"Please submit a valid pdf file")
            if vectordb:
                st.session_state.vectordb = vectordb
                st.session_state.pdf_name = pdf_name

    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    user_msg = st.chat_input("Enter your message here")
    if user_msg:
        # Show previous chat logs
        for chat in st.session_state.chat_log:
            with st.chat_message(chat["name"]):
                st.write(chat["msg"])

        # Display the latest user messages
        with st.chat_message(USER_NAME):
            st.write(user_msg)

        try:
            docs = st.session_state.vectordb.similarity_search(query=user_msg, k=2)
            doc_texts = [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        except Exception as e:
            st.error(f"Vector database not found: {str(e)}")

        # Get the response from GPT
        with st.spinner("Loading answer..."):
            response = response_chatgpt(user_msg, doc_texts, chat_history=st.session_state.chat_log)
        if response:
            with st.chat_message(ASSISTANT_NAME):
                assistant_msg = response["answer"]
                assistant_response_area = st.empty()
                assistant_response_area.write(assistant_msg)

                # Display the first source document
                st.write("### Sources")
                pdf_name = st.session_state.pdf_name if "pdf_name" in st.session_state else "Source unavailable"
                if response["sources"]:
                    # first_source = response["sources"][0]
                    for index, source in enumerate(response["sources"], start=1):
                        page_number = source["metadata"].get('page')
                        if page_number:
                            st.write(f"- File: {pdf_name}   Source {index} Page Number: {page_number}")
                        else:
                            st.write(f"- File: {pdf_name}   Source {index} Page Number: Unavailable")

                

            # Add chat logs to the session
            st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
            st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})

if __name__ == "__main__":
    main()

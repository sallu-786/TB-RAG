import os
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
from pdf_handler import handle_pdf_upload, fetch_or_create_vector_db


# Ensure environment variables are set
load_dotenv()

# Initialize the Azure OpenAI service
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
client = AzureOpenAI()

USER_NAME = "user"
ASSISTANT_NAME = "assistant"
model = "azure_openai_app"

st.title("TB Chat 007")  # Name of Application

def response_chatgpt(user_msg: str, input_documents, chat_history: list = []):
    system_msg = """You are an Assistant. Answer the questions based only on the provided documents. 
                    If the information is not in the documents, say you don't know."""
    messages = [{"role": "system", "content": system_msg}]

    # If there is a chat log, add it to the messages list
    if len(chat_history) > 0:
        for chat in chat_history:
            messages.append({"role": chat["name"], "content": chat["msg"]})

    # Add user message to messages list
    messages.append({"role": USER_NAME, "content": user_msg})

    # Append input documents to the messages list
    for doc in input_documents:
        messages.append({"role": "user", "content": f"Document snippet:\n{doc}"})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def main():
    # Sidebar for PDF upload
    with st.sidebar:
        st.title('PDF Chat Loader')
        pdf = st.file_uploader("Upload your PDF", type='pdf')
        file_name = handle_pdf_upload(pdf)
    
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

        if pdf:
            vectordb = fetch_or_create_vector_db(pdf, file_name)

            # Perform similarity search on the vector database
            docs = vectordb.similarity_search(query=user_msg, k=3)
            doc_texts = [doc.page_content for doc in docs]

            # Get the response from GPT
            with st.spinner("Loading answer..."):
                response = response_chatgpt(user_msg, doc_texts, chat_history=st.session_state.chat_log)
            if response:
                with st.chat_message(ASSISTANT_NAME):
                    assistant_msg = response.choices[0].message.content
                    assistant_response_area = st.empty()
                    assistant_response_area.write(assistant_msg)

                # Add chat logs to the session
                st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
                st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})

if __name__ == "__main__":
    main()

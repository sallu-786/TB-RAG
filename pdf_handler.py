import os
import streamlit as st
import pickle
from embeddings import get_pdf_text, get_text_chunks, create_embeddings, store_vector

def handle_pdf_upload(pdf):
    if pdf:
        file_name = pdf.name[:-4]
        if os.path.exists(f"{file_name}.pkl"):
            st.write("PDF file already exists.")
        else:
            st.write("File stored successfully.")
        return file_name
    return None

def fetch_or_create_vector_db(pdf, file_name):
    if os.path.exists(f"{file_name}.pkl"):
        with open(f"{file_name}.pkl", "rb") as f:
            with st.spinner("Fetching data from database"):
                vectordb = pickle.load(f)
    else:
        with st.spinner("Creating vector data"):
            text = get_pdf_text(pdf)
            chunks = get_text_chunks(text)
            vectordb = create_embeddings(chunks)
            vectordb = store_vector(vectordb, file_name)
    return vectordb

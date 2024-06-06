from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import pickle
import os

def get_pdf_text(file):  # get all text from pdf file
    pdf_reader = PdfReader(file)
    pages = []
    for i, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            pages.append((text, i + 1))  # store text with page number (1-based index)
    return pages


def get_text_chunks(pages):  # divide text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    chunks = []
    for text, page_number in pages:
        for chunk in text_splitter.split_text(text):
            chunks.append({"text": chunk, "page_number": page_number})
    return chunks


def create_embeddings(text_chunks):  # create vector embeddings for text chunks
    embeddings = HuggingFaceEmbeddings()  # If you have Open AI API key use this OpenAIEmbeddings()
    texts = [chunk['text'] for chunk in text_chunks]
    metadatas = [{'page': chunk['page_number']} for chunk in text_chunks]
    vector_base = FAISS.from_texts(texts, embeddings, metadatas=metadatas)   
    return vector_base


def store_vector(vectors, file_name):  # store vectors as pickle file, can also use langchain caching
    if os.path.exists(f"{file_name}.pkl"):
        with open(f"{file_name}.pkl", "rb") as f:
            vector_store = pickle.load(f)
    else:
        vector_store = vectors
        with open(f"{file_name}.pkl", "wb") as f:
            pickle.dump(vector_store, f)
    return vector_store

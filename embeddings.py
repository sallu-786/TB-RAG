from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import pickle
import os


def get_pdf_text(file):                             #get all text from pdf file
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):                          #divide text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def create_embeddings(text_chunks):                 #create vector embeddings for text chunks

                                                    # for japanese text,use this model in paranthesis of hugging face--
                                                    #---->model_name="intfloat/multilingual-e5-base"
    embeddings = HuggingFaceEmbeddings()            #If you have Open AI API key use this OpenAIEmbeddings()
    vector_base = FAISS.from_texts(text_chunks, embeddings)   
    return vector_base

def store_vector(vectors, file_name):               # store vectors as pickle file, can also use langchain caching
    if os.path.exists(f"{file_name}.pkl"):
        with open(f"{file_name}.pkl", "rb") as f:
            vector_store = pickle.load(f)
    else:
        vector_store = vectors
        with open(f"{file_name}.pkl", "wb") as f:
            pickle.dump(vector_store, f)
    return vector_store

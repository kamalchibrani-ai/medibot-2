from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def create_faiss_index(texts:list[str]):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return FAISS.from_texts(texts, embeddings)

def retrive_relevant_docs(vectorstore:FAISS, query:str, k:int=4):
    return vectorstore.similarity_search(query, k=k)


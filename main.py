import os
import time

import streamlit as st
from click import prompt

from utils.pdf_load import extract_text
from utils.vector import create_faiss_index , retrive_relevant_docs
from utils.chat_utils import get_chat_model , ask_chat_model
from utils.ui_utils import upload_pdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
EURI_API_KEY = os.getenv("EURI_API_KEY")

st.set_page_config(page_title="MedChatBot", page_icon=":robot_face:",
                   layout="wide", initial_sidebar_state="expanded")


st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
        color: black;
    }
    .chat-message .avatar {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    .chat-message .message {
        flex: 1;
    }
    .chat-message .timestamp {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #ff3333;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None
if "chat_model" not in st.session_state:
    st.session_state.chat_model = None

st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #ff4b4b; font-size: 3rem; margin-bottom: 0.5rem;">🏥 MediChat Pro</h1>
    <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Your Intelligent Medical Document Assistant</p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    uploaded_files = upload_pdf()

    if len(uploaded_files) >0 :
        st.write(len(uploaded_files) , "files uploaded successfully!")

        if st.button('process uploaded files',type='primary'):
            with st.spinner("Processing uploaded files"):
                all_txt = []
                for file in uploaded_files:
                    text = extract_text(file)
                    all_txt.append(text)

                #split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                chunks = []
                for text in all_txt:
                    chunks.extend(text_splitter.split_text(text))

                # create faiss index
                vectorstore = create_faiss_index(chunks)
                st.session_state.vectorstore = vectorstore

                #initialise chat model

                chat_model = get_chat_model(model='gpt-4.1-mini',temp=0.5 , api_key=EURI_API_KEY)
                st.session_state.chat_model = chat_model
                st.success("Documents processed successfully!")
                st.balloons()


st.markdown("### chat with your Documents")

#Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
        st.markdown(message['timestamp'])

#chat input

if prompt := st.chat_input("Ask about your medical documents..."):
    timestamp = time.strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp,
    })
    # Display user message
    with st.chat_message('user'):
        st.markdown(prompt)
        st.markdown(timestamp)

    if st.session_state.vectorstore and st.session_state.chat_model:
        with st.chat_message("assistant"):
            with st.spinner("Assistant Processing"):
                relevant_docs = retrive_relevant_docs(st.session_state.vectorstore, prompt)
                print(relevant_docs)
                # create context from the relevant docs

                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                print(context)
                # create prompt with context

                system_prompt = f"""You are MediChat Pro, an intelligent medical document assistant. 
                Based on the  medical documents uploaded, provide accurate and helpful answers. 
                If the information is not in the documents, clearly state that.
                
                Medical Documents:
                {context}
                
                user Question : {prompt}
                
                Ans = """

                response = ask_chat_model(st.session_state.chat_model, prompt)

            st.markdown(response)
            st.caption(timestamp)


            # add assistants message to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": timestamp,
            })
    else:
       st.chat_message("assistant")
       st.error("please upload files")
       st.caption(timestamp)






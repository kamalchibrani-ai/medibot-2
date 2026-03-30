import streamlit as st
from euriai.langchain import create_chat_model

def get_chat_model(model:str,temp:float,api_key:str):
    return create_chat_model(
        api_key=api_key,
        model=model,
        temperature=temp
    )
def ask_chat_model(chat_model , prompt:str):
    response = chat_model.invoke(prompt)
    return response.content




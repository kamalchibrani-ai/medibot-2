# here we will ask the user to load the pdfs using streamlit
import streamlit as st

def load_pdf():
    return st.file_uploader("upload pdfs here" , ['pdf'],True,help='you can upload multiple files here')


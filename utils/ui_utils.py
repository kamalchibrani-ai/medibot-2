import streamlit as st

def upload_pdf():
    return st.file_uploader("upload pdfs here" ,
                            ['pdf'],
                            True,
                            help='you can upload multiple files here')
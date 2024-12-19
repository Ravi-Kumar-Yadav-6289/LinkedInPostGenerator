from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()
llm = ChatGroq(groq_api_key=st.secrets["GROQ_API_KEY"], model="llama-3.2-3b-preview")


if __name__=="__main__":
    resp = llm.invoke("what are the main ingredients in omlet?")
    print(resp.content)

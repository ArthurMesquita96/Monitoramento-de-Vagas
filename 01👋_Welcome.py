import streamlit as st
import pandas as pd


st.set_page_config(page_title='Welcome', page_icon='👋', layout='wide')

st.markdown('# Bem-vindo ao dashboard de monitoramento de vagas')
st.markdown('## Aqui você encontra oportunidades na área de dados')

with st.container():
    
    st.text('\n')
    cols = st.columns(3, gap='large')

    with cols[0]:
        st.image('img/glassdoor_logo.png')

    with cols[1]:
        st.image('img/gupy_logo.png')
    
    with cols[2]:
        st.image('img/vagas_logo.png')
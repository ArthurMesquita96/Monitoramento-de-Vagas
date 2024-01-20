import page1_welcome
import page2_skills
import page3_locals
import page4_levels
import streamlit as st
import pandas as pd

if __name__ == '__main__':
    st.set_page_config(layout='wide')

    # importando dados
    data =  pd.read_excel('vagas_clean.xlsx')

    # Definindo páginas
    PAGES = {
        "👋 Welcome!": page1_welcome,
        "🪓 Skills!": page2_skills,
        "📍 Locals!": page3_locals,
        "💼 Level!": page4_levels
    }

    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page.app(data)
import streamlit as st
import pandas as pd

data = pd.read_excel('data/data_clean/vagas_clean.xlsx')


st.markdown('# Levels')

df_seniority = ( data[['senioridade', 'link']]
                    .groupby('senioridade').count()
                    .reset_index()
                    .sort_values('link', ascending=False)
                    .rename(columns={'link': 'count'}) 
            )

st.bar_chart(data = df_seniority, x = 'senioridade', y = 'count')
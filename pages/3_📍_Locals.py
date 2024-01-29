import streamlit as st
import pandas as pd

data = pd.read_excel('data/data_clean/vagas_clean.xlsx')

st.markdown('# Locals')

df_city = ( data[['cidade', 'link']]
            .groupby('cidade')
            .count()
            .reset_index()
            .sort_values('link', ascending=False)
            .rename(columns={'link': 'count'}) 
        )

df_state = ( data[['estado', 'link']]
            .groupby('estado')
            .count()
            .reset_index()
            .sort_values('link', ascending = False)
            .rename(columns={'link': 'count'}) 
        )

st.bar_chart(data = df_city, x = 'cidade', y = 'count')

st.bar_chart(data = df_state, x = 'estado', y = 'count')

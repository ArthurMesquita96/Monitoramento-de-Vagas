import streamlit as st
import pandas as pd

data = pd.read_excel('data/data_clean/vagas_vagas_clean.xlsx')

st.markdown('# Locals')

df_city = ( data[['cidade', 'link_site']]
            .groupby('cidade')
            .count()
            .reset_index()
            .sort_values('link_site', ascending=False)
            .rename(columns={'link_site': 'count'}) 
        )

df_state = ( data[['estado', 'link_site']]
            .groupby('estado')
            .count()
            .reset_index()
            .sort_values('link_site', ascending = False)
            .rename(columns={'link_site': 'count'}) 
        )

st.bar_chart(data = df_city, x = 'cidade', y = 'count')

st.bar_chart(data = df_state, x = 'estado', y = 'count')

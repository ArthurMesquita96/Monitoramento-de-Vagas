import streamlit as st

def app(data):
    st.write('Locals')

    df_aux = data[['cidade','link']].groupby('cidade').count().reset_index().sort_values('link', ascending = False).rename(columns={'link': 'count'})
    df_aux2 = data[['estado','link']].groupby('estado').count().reset_index().sort_values('link', ascending = False).rename(columns={'link': 'count'})

    st.bar_chart(data = df_aux, x = 'cidade', y = 'count')
    st.bar_chart(data = df_aux2, x = 'estado', y = 'count')

    return None
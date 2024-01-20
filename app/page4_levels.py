import streamlit as st

def app(data):
    st.write('Levels')

    df_aux = data[['senioridade', 'link']].groupby('senioridade').count().reset_index().sort_values('link', ascending=False).rename(columns={'link':'count'})

    st.bar_chart(data = df_aux, x = 'senioridade', y = 'count')

    return None
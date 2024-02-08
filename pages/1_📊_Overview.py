import pandas    as pd
import streamlit as st

data = pd.read_excel('data/data_clean/vagas_clean.xlsx')


st.markdown('# Welcome')

senioridade_option = st.multiselect(label = 'Senioridade',options = data['senioridade'].unique())
cidade_option = st.multiselect(label = 'Cidade', options = data['cidade'].unique())
estado_option = st.multiselect(label = 'Estado', options = data['estado'].unique())
modalidade_option = st.multiselect(label = 'Modalidade', options = data['modalidade'].unique())
contrato_option = st.multiselect(label = 'Contrato', options = data['contrato'].unique())


dict_filter = {
        'senioridade': senioridade_option,
        'modalidade': modalidade_option,
        'contrato': contrato_option,
        'cidade': cidade_option,
        'estado': estado_option
    }

for column_name, selected_option in dict_filter.items():
    if selected_option:
        data = data.loc[data[column_name] == selected_option[0]]


st.dataframe(data, height=500)


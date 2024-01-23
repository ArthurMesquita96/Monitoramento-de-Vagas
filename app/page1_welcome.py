import streamlit as st

def app(data):
    st.write('Welcome')
    senioridade_option = st.multiselect(label = 'Senioridade',options = data['senioridade'].unique())
    cidade_option = st.multiselect(label = 'Cidade',options = data['cidade'].unique())
    estado_option = st.multiselect(label = 'Estado',options = data['estado'].unique())
    modalidade_option = st.multiselect(label = 'Modalidade',options = data['modalidade'].unique())
    contrato_option = st.multiselect(label = 'Contrato',options = data['contrato'].unique())

    dict_filter = {
            'senioridade':senioridade_option,
            'modalidade':modalidade_option,
            'contrato':contrato_option,
            'cidade': cidade_option,
            'estado': estado_option
        }

    def verifica_filtros_vazios(dict_filter):

        for coluna, filtro in dict_filter.copy().items():
            if filtro == []:
                dict_filter.pop(coluna)

        return dict_filter

    def filtra_coluna(data, coluna, filtro):
        if filtro != []:
            df_filtrado = data.loc[
                data[coluna].isin(filtro)
            ]
        else:
            df_filtrado = data
        return df_filtrado

    def filtra_todas_as_colunas(data,dict_filter):
        filtros_selecionados = verifica_filtros_vazios(dict_filter)
        for coluna, filtro in filtros_selecionados.items():
            data = filtra_coluna(data, coluna, filtro)

        return data
    
    df_filter = filtra_todas_as_colunas(data,dict_filter)

    st.dataframe(df_filter, height=500)

    return None
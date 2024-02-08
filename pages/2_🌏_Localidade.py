import re
import pandas    as pd
import streamlit as st
import geopandas as gpd

import branca
import folium
from streamlit_folium import folium_static


def adjust_states_names(state_name: str) -> str:
    # adiciona espaço onde há letras maiusculas
    state_name = re.sub(r'(?<=\w)([A-Z])', r' \1', state_name)  # 'RioGrandedoSul' -> 'Rio Grandedo Sul'

    # adiciona espaço se as substring 'do'/'de' estão no final de uma palavra ( seguidas por espaço )
    state_name = re.sub(r'(d[oe])(?=\s)', r' \1', state_name)   # 'Rio Grandedo Sul' -> 'Rio Grande do Sul'

    return state_name



def plot_brazil_map(data_map):

    colormap = branca.colormap.LinearColormap(
                    vmin=data_map['percentage'].quantile(0.0),
                    vmax=data_map['percentage'].quantile(1),
                    colors=["red", "orange", "lightblue", "green", "darkgreen"],
                    caption="Porcentagem de vagas no estado (%)",
                )
    
    m = folium.Map([-15, -50], zoom_start=4)

    popup = folium.GeoJsonPopup(
                    fields=['geo_state', 'vagas', 'percentage'],
                    aliases=['Estado', 'Vagas', 'Porcentagem (%)'],
                    localize=True,
                    labels=True,
                    style='background-color: yellow',
                )

    tooltip = folium.GeoJsonTooltip(
                    fields=['geo_state', 'vagas', 'percentage'],
                    aliases=['State:', 'Vagas:', 'Porcentagem (%):'],
                    localize=True,
                    sticky=False,
                    labels=True,
                    style="""
                        background-color: #F0EFEF;
                        border: 2px solid black;
                        border-radius: 3px;
                        box-shadow: 3px;
                    """,
                    max_width=800,
                )

    g = folium.GeoJson(
                    data=data_map,
                    style_function=lambda x:{
                        'fillColor': colormap(x['properties']['percentage'])
                        if x['properties']['percentage'] is not None
                        else 'transparent',
                        'color': 'black',
                        'fillOpacity': 0.4,
                    },
                    popup=popup,
                    tooltip=tooltip,
            ).add_to(m)

    colormap.add_to(m)

    folium_static(m, width=900, height=500)

    return None


st.markdown('# Localidade')

gdf = gpd.read_file('data/data_raw/tmp/data_json/geo_data_brazil.json')

geodata = gdf[['NAME_1', 'geometry']].rename(columns={'NAME_1': 'geo_state'})

df_vagas = pd.read_excel('data/data_clean/vagas_vagas_clean.xlsx')

df_state = ( df_vagas[['estado', 'site_da_vaga']]
                    .groupby('estado')
                    .count()
                    .reset_index()
                    .rename(columns={'site_da_vaga': 'vagas'})
        )


state_uf = {
            'Acre': 'AC',
            'Alagoas': 'AL',
            'Amazonas': 'AM',
            'Amapá': 'AP',
            'Bahia': 'BA',
            'Ceará': 'CE',
            'Distrito Federal': 'DF',
            'Espírito Santo': 'ES',
            'Goiás': 'GO',
            'Maranhão': 'MA',
            'Mato Grosso': 'MT',
            'Mato Grosso do Sul': 'MS',
            'Minas Gerais': 'MG',
            'Pará': 'PA',
            'Paraíba': 'PB',
            'Paraná': 'PR',
            'Pernambuco': 'PE',
            'Piauí': 'PI',
            'Rio de Janeiro': 'RJ',
            'Rio Grande do Norte': 'RN',
            'Rio Grande do Sul': 'RS',
            'Rondônia': 'RO',
            'Roraima': 'RR',
            'Santa Catarina': 'SC',
            'São Paulo': 'SP',
            'Sergipe': 'SE',
            'Tocantins': 'TO'
    }

geodata['geo_state'] = geodata['geo_state'].apply(lambda state: adjust_states_names(state))

geodata['uf'] = geodata['geo_state'].map( state_uf )


df_full = pd.merge(left=geodata, right=df_state, how='left', left_on='uf', right_on='estado')

df_full['percentage'] = 100 * df_full['vagas'] / df_full['vagas'].sum()


plot_brazil_map(df_full)
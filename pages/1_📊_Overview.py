import re
import folium
import branca
import pandas         as pd
import streamlit      as st
import geopandas      as gpd
import plotly.express as px

from PIL              import Image
from streamlit_folium import folium_static


st.set_page_config(page_title='Overview', page_icon='📊', layout='wide')

### Senioridade #######

def platform_job_position_count(data: pd.DataFrame, platform: str) -> pd.DataFrame:
    df_platform = data.query('site_da_vaga == @platform')

    df_platform = ( df_platform[['posicao', 'site_da_vaga']]
                        .groupby('posicao')
                        .count()
                        .reset_index()
                        .rename(columns={'site_da_vaga': 'vagas'}) 
                    )
    return df_platform

def senioridade_job_position_count(data: pd.DataFrame, position: str) -> pd.DataFrame:
    df_level = data.query('posicao == @position')

    df_level = ( df_level[['senioridade', 'site_da_vaga']]
                        .groupby('senioridade')
                        .count()
                        .reset_index()
                        .rename(columns={'site_da_vaga': 'vagas'}) 
                    )
    return df_level

def platform_bar_graph(data: pd.DataFrame) -> None:
    
    fig = px.bar( data, x='senioridade', y='vagas', title='Vagas por Senioridade')

    st.plotly_chart(fig, use_container_width=True)
    
    return None

#######################
# Mapa
######################
def adjust_states_names(state_name: str) -> str:

    # adiciona espaço onde há letras maiusculas
    state_name = re.sub(r'(?<=\w)([A-Z])', r' \1', state_name)  # 'RioGrandedoSul' -> 'Rio Grandedo Sul'

    # adiciona espaço se as substring 'do'/'de' estão no final de uma palavra ( seguidas por espaço )
    state_name = re.sub(r'(d[oe])(?=\s)', r' \1', state_name)   # 'Rio Grandedo Sul' -> 'Rio Grande do Sul'

    return state_name

def get_geographical_data(data: pd.DataFrame) -> pd.DataFrame:

    geodata = gpd.read_file('data/data_raw/tmp/data_json/geo_data_brazil.json')

    geodata = geodata[['NAME_1', 'geometry']].rename(columns={'NAME_1': 'geo_state'})

    df_state = ( data[['estado', 'site_da_vaga']]
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


    df_map = pd.merge(left=geodata, right=df_state, how='left', left_on='uf', right_on='estado')

    df_map['percentage'] = 100 * df_map['vagas'] / df_map['vagas'].sum()

    return df_map

def plot_brazil_map(data_map: pd.DataFrame) -> None:

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

#########################
### Skills 
#####################
def get_skills_list(data: pd.DataFrame) -> set:
    unique_skills = set()

    for _, row in data.iterrows():
        
        try:
            lista_skills = re.findall(r'\'(.*?)\'', row['skills'])
            
            unique_skills.update(lista_skills)
        except:
            continue

    return unique_skills

def get_skills_dataframe(data: pd.DataFrame, skills_list: list, columns: list) -> pd.DataFrame:
    data_list = []

    for _, row in data.iterrows():
        row_skills = []

        try:
            for skill in skills_list:
                if skill in row['skills']:
                    row_skills.append(True)
                else:
                    row_skills.append(False)
        except:
            pass

        row_skills = [row['codigo_vaga'], row['site_da_vaga']] + row_skills
        
        data_list.append(row_skills)

    return pd.DataFrame(data=data_list, columns=columns)

def plot_bar_graph(data: pd.DataFrame, top_skills: int) -> None:

    series_aux = ( data.drop(['codigo_vaga', 'site_da_vaga'], axis=1)
                    .sum()
                    .sort_values(ascending=False)
            )
    
    series_aux = series_aux.iloc[:top_skills] 

    fig = px.bar(
            x=series_aux.index,
            y=series_aux.values,
            labels={'x': 'Skills', 'y': 'Número de Vagas'},
            title=f'Top {top_skills} Skills por Vagas'
        )

    st.plotly_chart(fig, use_container_width=True)

    return None

#######################
### Benefits 
######################

def get_benefits_list(data: pd.DataFrame) -> set:
    unique_benefits = set()

    for _, row in data.iterrows():
        
        try:
            lista_beneficios = re.findall(r'\'(.*?)\'', row['beneficios'])
            
            unique_benefits.update(lista_beneficios)
        except:
            continue

    return unique_benefits

def get_benefits_dataframe(data: pd.DataFrame, benefits_list: list, columns: list) -> pd.DataFrame:
    data_list = []

    for _, row in data.iterrows():
        row_benefits = []

        try:
            for benefit in benefits_list:
                if benefit in row['beneficios']:
                    row_benefits.append(True)
                else:
                    row_benefits.append(False)
        except:
            pass

        row_benefits = [row['codigo_vaga'], row['site_da_vaga']] + row_benefits
        
        data_list.append(row_benefits)

    return pd.DataFrame(data=data_list, columns=columns)

def plot_bar_graph(data: pd.DataFrame, top_benefits: int) -> None:

    series_aux = ( data.drop(['codigo_vaga', 'site_da_vaga'], axis=1)
                    .sum()
                    .sort_values(ascending=False)
            )
    
    series_aux = series_aux.iloc[:top_benefits] 

    fig = px.bar(
            x=series_aux.index,
            y=series_aux.values,
            labels={'x': 'Benefícios', 'y': 'Número de Vagas'},
            title=f'Top {top_benefits} Beneficios por Vagas'
        )

    st.plotly_chart(fig, use_container_width=True)

    return None


# =====================================================================================
# Sidebar (Barra Lateral)
# =====================================================================================

st.sidebar.markdown('# Monitoramento de Vagas')
st.sidebar.markdown('### Aqui você não perde nada!')

cds_logo = Image.open('img/cds.png')
st.sidebar.image(cds_logo, width=150)

st.sidebar.markdown('''---''')

powered_cds_logo = Image.open('img/comunidade_ds_logo.png')
st.sidebar.image(powered_cds_logo, width=250)
st.sidebar.markdown('### Powered by Comunidade DS')


# =====================================================================================
# Layout streamlit
# =====================================================================================


df_raw = pd.read_excel('data/data_refined/vagas_full.xlsx')


st.markdown('# Overview')

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric('Analista de Dados', df_raw.loc[df_raw['posicao'] == 'Analista de Dados'].shape[0], 'X novas vagas')
metric2.metric('Cientista de Dados',df_raw.loc[df_raw['posicao'] == 'Cientista de Dados'].shape[0], 'X novas vagas')
metric3.metric('Engenheiro de Dados', df_raw.loc[df_raw['posicao'] == 'Engenheiro de Dados'].shape[0] , 'X novas vagas')
metric4.metric('Total', df_raw.shape[0], 'X novas vagas')

st.markdown('## Senioridades por Posição')

glassdor_tab, gupy_tab, vagascom_tab = st.tabs(['Analista de Dados', 'Cientista de Dados', 'Engenheiro de Dados'])

with glassdor_tab:

    cols = st.columns([1, 7])
    with cols[0]:
        # st.markdown('#')
        # st.markdown('## Posição')
        # st.image('img/glassdoor_logo.png', width=200)

        df_level = senioridade_job_position_count(df_raw, 'Analista de Dados')
        # st.dataframe(df_level)

    with cols[1]:
        platform_bar_graph(df_level)

with gupy_tab:
    cols = st.columns([1, 7])
    with cols[0]:
        # st.markdown('#')
        # st.markdown('## Posição')
        # st.image('img/gupy_logo.png', width=200)

        df_level = senioridade_job_position_count(df_raw, 'Cientista de Dados')
        # st.dataframe(df_level)
        
    with cols[1]:
        platform_bar_graph(df_level)

with vagascom_tab:
    cols = st.columns([1, 7])

    with cols[0]:
        # st.markdown('#')
        # st.markdown('## Posição')
        # st.image('img/vagas_logo.png', width=200)

        df_level = senioridade_job_position_count(df_raw, 'Analista de Dados')
        # st.dataframe(df_level)

    with cols[1]:
        platform_bar_graph(df_level)


st.markdown('## Habilidades por Posição')

skills = list( get_skills_list(df_raw) )
skills.sort()
columns = ['codigo_vaga', 'site_da_vaga'] + skills
df_skills = get_skills_dataframe(df_raw, skills, columns)
plot_bar_graph(df_skills, 15)

st.markdown('## Benefícios por Posição')

benefits = list( get_benefits_list(df_raw) )
benefits.sort()
columns = ['codigo_vaga', 'site_da_vaga'] + benefits
df_benefits = get_benefits_dataframe(df_raw, benefits, columns)
plot_bar_graph(df_benefits, 15)

st.markdown('#')
st.markdown('# Visão Geral Brasil')

df_map = get_geographical_data(df_raw)

plot_brazil_map(df_map)
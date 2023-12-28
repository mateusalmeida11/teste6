## importando bibliotecas: 

import pandas as pd
from haversine import haversine
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import folium
from streamlit_folium import folium_static
from datetime import datetime

st.set_page_config(page_title='Visão Entregadores',page_icon='🚚',layout='wide')


# --------------------------
# funções
# --------------------------

def top_delivers (df,operation):
        
    """ Esta função tem a responsabilidade de verificar os entregadores mais rápidos e os mais lentos
    
        1. Ela recebe dois parâmetros
        2. Parâmetro df que é o dataframe onde será feita a operação
        3. Parâmetro operation que recebe max e min
        4. A partir do parâmetro ela ordenará o dataframe
        5. Faz um agrupamento dinâmico para retornar a lista com os maiores e menores tempos
        
    """ 
                
    if operation == 'max':
                
        ## vamos classificar nosso dataframe pelos mais lentos utilizando o parâmetro max() e ascending False;

        df_classificado = (df.loc[:,['City','Delivery_person_ID','Time_taken(min)']]
                             .groupby(['Delivery_person_ID','City'])
                             .max()
                             .sort_values(['City','Time_taken(min)'],ascending=False)
                             .reset_index())
        
    elif operation == 'min': 
                    
        ## vamos classificar nosso dataframe pelos mais rápidos utilizando o método min e o sort values

        df_classificado = (df.loc[:,['City','Delivery_person_ID','Time_taken(min)']]
                             .groupby(['Delivery_person_ID','City'])
                             .min()
                             .sort_values(['City','Time_taken(min)'])
                             .reset_index())                                   
                    
    ## vamos extrair o nome das cidades em uma lsita para trabalharmos de uma maneira dinâmica

    list_city = list(df['City'].unique())

    ## fazendo o for para percorrermos a lista de cidades e filtrarmos propriamente dito no dataframe. Além disso utilizaremos
    ## o head(10) para pegar apenas os 10 por cidades

    list_df = [df_classificado.loc[df_classificado['City'] == city,:].head(10) for city in list_city]

    df_concat = pd.concat(list_df).reset_index(drop=True)
                
    return df_concat

            
def calcule_big_number(df, col, operation): 
    
    """ Esta função tem a responsabilidade de calcular máximos e mínimos
    
        1. Ela recebe dois parâmetros
        2. Parâmetro max para retornar o valor máximo de uma coluna
        3. Parâmetro min para retornar o valor mínimo de uma coluna
        
    """ 
                
    if operation == 'max':
                    
        results = df[col].max()
                    
    elif operation == 'min': 
                    
        results = df[col].min()
                    
    return results

def clean_code(df):
    
    """ Esta função tem a responsabilidade de limpar o dataframe 
    
        Tipos de limpeza:
        
        1. Remoção de dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Outpou: Dataframe
    
    """

    ## removendo os espaços vazios das células

    columns = list(df.columns)

    for column in columns: 

        try: 

            df.loc[:,column] = df.loc[:,column].str.strip()

        except: 

            df.loc[:,column] = df.loc[:,column]

    ## removendo todos os NaN 

    for column in columns: 

        try: 

            df = df.loc[df[column]!='NaN',:]

        except: 

            df.loc[:,column] = df.loc[:,column]
    ## limpando o (min) da coluna Time_taken (min)

    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    
    ## fazendo transformação dos dados: 

    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )
    df['Order_Date'] = pd.to_datetime( df['Order_Date'],format = '%d-%m-%Y' )

    ## criando uma coluna para semana: 

    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')

    ## resetando o index: 

    df = df.reset_index(drop=True)
    
    return df

## importando o dataset: 

df = pd.read_csv('dataset/train.csv')

## cleaning dataset

df = clean_code ( df )

## ===================================================================================

## barra lateral

## ===================================================================================

st.header( 'Marketplace - Visão Entregadores' )

#image_path = image_path = Path.home()/'Desktop'/'Meigaron'/'Streamlit'/'Streamlit 1'/'logo.png'
image = Image.open('logo.png')

st.sidebar.image(image,width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022,4,13),
    min_value=datetime(2022,2,1),
    max_value=datetime(2022,4,6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default = ['Low','Medium','High','Jam'] )

st.sidebar.markdown("""---""")


weather_options = st.sidebar.multiselect(
    'Quais as condições de Clima',
    ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
    default = ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'] )

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

## Filtro de data: 

linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas,:]

## Filtro de trânsito: 

linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas,:]

## Filtro de Condição Climática

linhas_selecionadas = df['Weatherconditions'].isin( weather_options )
df = df.loc[linhas_selecionadas, :]


## ===================================================================================

## layout streamlit

## ===================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1: 
    
    with st.container(): 
        
        st.title('Overall Metric')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1: 
            
            maior_idade =  calcule_big_number(df,'Delivery_person_Age',operation='max')
            
            col1.metric('Maior Idade',maior_idade)
            
        with col2: 
            
            menor_idade = calcule_big_number(df,'Delivery_person_Age',operation='min')
        
            col2.metric('Menor de Idade',menor_idade)
        
        with col3: 
            
            melhor_condicao = calcule_big_number(df,'Vehicle_condition',operation='max')
            
            col3.metric('Melhor Condição',melhor_condicao)
            
        with col4: 
            
            pior_condicao = melhor_condicao = calcule_big_number(df,'Vehicle_condition',operation='min')
            
            col4.metric('Pior Condição',pior_condicao)
            
    with st.container(): 
        
        st.markdown("""---""")
        
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1: 
            
            st.markdown('##### Avaliação Médias por Entregador')
            
            df_avg_per_delivery = df.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            
            st.dataframe(df_avg_per_delivery)
            
        with col2: 
            
            st.markdown('##### Avaliação Média por Trânsito')
            
            df_avg_std_per_traffic = (df.loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                                        .groupby('Road_traffic_density')
                                        .agg({'Delivery_person_Ratings':['mean','std']}))
            
            df_avg_std_per_traffic.columns = ['delivery_mean','delivery_std']
            df_avg_std_per_traffic.reset_index()
            
            st.dataframe(df_avg_std_per_traffic)
            
            st.markdown('##### Avaliação Média por Clima')
            
            df_avg_std_per_wheatherconditions = (df.loc[:,['Weatherconditions','Delivery_person_Ratings']]
                                                    .groupby('Weatherconditions')
                                                    .agg({'Delivery_person_Ratings':['mean','std']}))

            df_avg_std_per_wheatherconditions.columns = ['delivery_mean','delivery_std']

            df_avg_std_per_wheatherconditions.reset_index()
            
            st.dataframe(df_avg_std_per_wheatherconditions)
            
def avaliacao (df,col_selecionada):
            
            
            
    with st.container(): 
        
        st.markdown("""---""")
        
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        
        with col1:
            
            st.markdown('##### Top Entregadores Mais Rápidos')
            df_concat_fast = top_delivers(df,operation='min')
            st.dataframe(df_concat_fast)
            
        with col2: 
            
            st.markdown('##### Top Entregadores Mais Lentos')
            df_concat_slow = top_delivers(df,operation='max')
            st.dataframe(df_concat_slow)         
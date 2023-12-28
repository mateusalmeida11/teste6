## importando bibliotecas: 

import pandas as pd
import numpy as np
from haversine import haversine
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import folium
from streamlit_folium import folium_static
from datetime import datetime

st.set_page_config(page_title='Visão Restaurantes',page_icon='🍽️',layout='wide')

# ------------------------------------------
# Funções
# ------------------------------------------

def avg_std_time_on_traffic ( df ):
            
    df_aux = (df.loc[:,['City','Time_taken(min)','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .agg({'Time_taken(min)':['mean','std']}))

    df_aux.columns = ['mean','std']

    df_aux = df_aux.reset_index()
            
    fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='mean',
                      color='std',color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std']))
                
    return fig

def avg_std_time_graph ( df ):

    df_time_mea_std = df.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})

    df_time_mea_std.columns=['mean','std']

    df_time_mea_std = df_time_mea_std.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar( name = 'Control', x = df_time_mea_std['City'], y = df_time_mea_std['mean'], error_y=dict(type='data',array=df_time_mea_std['std'])))

    fig.update_layout(barmode='group')
                
    return fig

def time_festival (df,festival,operation): 
    
    """ Esta função tem como objetivo calcular média e desvio padrão com e sem festival
    
        1. Ela recebe três parâmetros: dataframe, festival e a operação a ser feita;
        2. Parâmetros para festival é: 'Yes' ou 'No';
        3. Parâmetros para operation é: avg_time ou std_time
        4. A função retorna a média ou desvio padrão com ou sem festival
    
    """
            
    df_aux = df.loc[:,['Festival','Time_taken(min)']].groupby('Festival').agg({'Time_taken(min)':['mean','std']})

    df_aux.columns = ['avg_time','std_time']

    df_aux = df_aux.reset_index()
            
    df_aux = df_aux.loc[df_aux['Festival'] == festival,operation]
                
    result = np.round(df_aux,2)
                
    return result

def distance (df,operation):
    
    """ Esta função tem como objetivo calcular a distância média dos restaurantes até os pontos de entrega
    
        1. Parâmetros de entrada: 
        
            df = Dataframe onde será realizada as operações;
            operation = qual operação que será realizada; 
            
                - 'mean' = calcula a média de todas as distâncias; 
                - 'graph' = plota um gráfico com a média das distâncias por Cidade;
                
        2. Parâmetros de saída: 
        
            Vamos ter dois parâmetros de saída a depender da operação realizada; 
            
            - Saída 'mean' = retorna um número que é a média entre todas as distâncias;
            
            - Saída 'graph' = retorna um gráfico de pizza com a distância média por cidade;
    
    """
            
    colunas = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']

    df['distance'] = df.loc[:,colunas].apply(lambda x:
                        haversine(
                        (x['Restaurant_latitude'],x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
    
    if operation == 'mean':
            
        avg_distance = np.round(df.loc[:,['distance']].mean(),2)
                
        return avg_distance
    
    if operation == 'graph':
        
        avg_distance = df.loc[:,['City','distance']].groupby('City').mean().reset_index()
        
        fig = go.Figure( data=[ go.Pie( labels = avg_distance['City'], values = avg_distance['distance'], pull = [0, 0.1,0])])
        
        return fig 

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

st.header( 'Marketplace - Visão Restaurantes' )

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
        
        
        st.title('Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            
            delivery_unique = len(df["Delivery_person_ID"].unique())
        
            col1.metric('Entregadores únicos',delivery_unique)
            
        with col2:
            
            avg_distance = distance(df,'mean')
            
            col2.metric('A distância média das entregas',avg_distance)
        
        with col3:
            
            avg_time_festival = time_festival(df,'Yes','avg_time')
            
            col3.metric('Tempo médio de entrega com Festival', avg_time_festival)
        
        with col4: 
            
            std_time_festival = time_festival(df,'Yes','std_time')
            
            col4.metric('Desvio Padrão Médio de entrega com festival',std_time_festival)
            
        with col5: 
            
            avg_time_no_festival = time_festival(df,'No','avg_time')
            
            col5.metric('Tempo médio de entrega sem Festival',avg_time_no_festival)

            
        with col6:
            
            std_time_no_festival = time_festival(df,'No','std_time')
            
            col6.metric('STD Médio de entrega sem festival', std_time_no_festival)
        
        
    with st.container(): 
        
        st.markdown("""---""")
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            fig = avg_std_time_graph ( df )

            st.plotly_chart( fig )  
            
        with col2: 

            df_aux = df.loc[:,['City','Type_of_order','Time_taken(min)']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})

            df_aux.columns = ['mean','std']

            df_aux = df_aux.reset_index()

            st.dataframe(df_aux)
                    
            
        
    with st.container():
        
        st.markdown("""---""")
        
        col1, col2, col3 = st.columns(3)
        
        with col1: 
        
            fig = distance(df,'graph')
            st.plotly_chart( fig )            
            
        with col2: 
            
            fig = avg_std_time_on_traffic(df)
            
            st.plotly_chart( fig )
            

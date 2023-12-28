## importando bibliotecas: 

import pandas as pd
import numpy as np
from haversine import haversine
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from PIL import Image
from streamlit_folium import folium_static
from datetime import datetime

st.set_page_config(page_title='Visão Empresa',page_icon='📈',layout='wide')

# --------------------------
# funções
# --------------------------

def order_metric(df): 

    ## Vamos selecionar as colunas Order_Date e ID, fazendo a contagem pelos "ID" para entendermos quantos pedidos por dia

    df_aux = df.loc[:,['Order_Date','ID']].groupby('Order_Date').count().reset_index()

    ## fazendo o gráfico de barras

    fig = px.bar(df_aux,x='Order_Date',y='ID')
            
    return fig

def traffic_order_share(df):
                
                
    df_aux = (df.loc[:,['ID','Road_traffic_density']]
                .groupby('Road_traffic_density')
                .count()
                .reset_index())
    
    df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()
    fig = px.pie(df_aux,values='entregas_perc',names='Road_traffic_density')
                    
    return fig

def traffic_order_city( df ):

    df_aux = (df.loc[:,['ID','City','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .count()
                .reset_index())
    fig = px.scatter(df_aux,x='City',y='Road_traffic_density',size='ID')
    return fig

        
def order_by_week(df):
    
        
    df_aux = df.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year',y='ID')
            
    return fig

def order_share_by_week(df):
        
    df_aux01 = (df.loc[:,['ID','week_of_year']]
                    .groupby('week_of_year')
                    .count()
                    .reset_index())
            
    df_aux02 = (df.loc[:,['Delivery_person_ID','week_of_year']]
                    .groupby('week_of_year')
                    .nunique()
                    .reset_index())
            
    df_aux = pd.merge(df_aux01,df_aux02,how='inner')
    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
            
    return fig

def country_maps(df):
    
    
    df_aux = (df.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                .groupby(['City','Road_traffic_density'])
                .median()
                .reset_index())
       
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():

        folium.Marker([location_info['Delivery_location_latitude'],
                location_info['Delivery_location_longitude']],
                popup=location_info[['City','Road_traffic_density']]).add_to(map)
        
    folium_static(map, width=1024, height=600)
        
    return None       

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

# ------------------------- Inicio da Estrutura Lógica do Código --------------------------------------------------------------------------------------

# --------------------------
# importando o dataset:
# --------------------------

df = pd.read_csv('dataset/train.csv')

#image_path = image_path = Path.home()/'Desktop'/'Meigaron'/'Streamlit'/'Streamlit 1'/'logo.png'



# --------------------------
# limpando os dados:
# --------------------------

df = clean_code(df)


## ===================================================================================

## barra lateral

## ===================================================================================

st.header('Marketplace - Visão Cliente')

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
    default = 'Low')

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

## Filtro de data: 

linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas,:]

## Filtro de trânsito: 

linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas,:]



## ===================================================================================

## layout streamlit

## ===================================================================================

## vamos criar abas 

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])


## tudo que tiver identado, vai ficar dentro do tab1
with tab1: 
    
    ## o container vai dividir o dashboard em alguns retângulos
    
    with st.container():
        
        fig = order_metric(df)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig,use_container_with = True) 

        ## use_container_with singifica usar a largura do container 
        
        with st.container(): 
        
            ## vamos usar o columns para conseguirmos dividir um container em dois 
            col1, col2 = st.columns(2)
            
            with col1:
                
                fig = traffic_order_share( df )
                st.header('Traffic Order Share')
                st.plotly_chart(fig,use_container_with = True)
                                
            with col2: 
                
                st.header('Traffic Order City')
                fig = traffic_order_city( df )
                st.plotly_chart(fig,use_container_with = True)               
    
with tab2: 
    
    with st.container():
        
        st.markdown('# Order by Week')
        fig = order_by_week(df)
        st.plotly_chart(fig,use_container_with = True)

        
    with st.container(): 
        
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df)
        st.plotly_chart(fig,use_container_with = True)
        

        
    
with tab3: 
    
    st.markdown('# Country Maps')
    
    country_maps( df )
    

    
    























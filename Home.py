import streamlit as st
from PIL import Image
from pathlib import Path

st.set_page_config (
    page_title = 'Home',
    page_icon = '🎲'
    
)


#image_path = image_path = Path.home()/'Desktop'/'Meigaron'/'Streamlit'/'Streamlit 1'/'logo.png'
image = Image.open('logo.png')

st.sidebar.image(image, width=120) 

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown (

    """
    
    Growth Dashboard foi construído para acompanhas as métricas de crescimento dos Entregadores e Restaurantes
    ### Como utilizar esse Growth Dashboard? 
    
    - Visão Empresa: 
    
        - Visão Gerencial: Métricas de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visao Geográfica: Insights de geolocalização.
        
    - Visão Entregador: 
    
        - Acompanhamento dos indicadores semanais de crescimento. 
        
    - Visão Restaurante: 
    
        - Indicadores semanais de crescimento dos restaurantes 
        
    ### Ask for Help
    
    - Time de Data Science no Discord 
    
        -@mateus
        
    """
    

)
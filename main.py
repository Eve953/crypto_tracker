import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")

def get_data():
    ids = "bitcoin,tether,ethereum,solana, usdc"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"
    
    response = requests.get(url)
    return response.json()

def get_fear_n_greed():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    fng = response.json()['data'][0]
    return fng['value'], fng['value_classification']
    
fng_val, fng_label = get_fear_n_greed()

st.title("Crypto Analysis Dashboard")

# The inputs
with st.expander("➕ Add New Asset to Portfolio"):
    input_col1, input_col2, input_col3 = st.columns([2, 2, 1])
    with input_col1:
        coin = st.selectbox("Ticker", ["BTC", "ETH", "USDC", "SOL", "USDT"])
    with input_col2:
        amount = st.number_input("Amount ($)", min_value=0.0)
    with input_col3:
        st.write(" ") 
        add_btn = st.button("Update Dashboard")

# The Metric Grid
# horizontal block for divs
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Fear & Greed", fng_val, fng_label)
with m2:
    st.metric("Risk Level", "Low", "Stable")
with m3:
    st.metric("Top Performer", "SOL", "+12%")
with m4:
    st.metric("24h Volume", "$2.4B", "-0.5%")


# THE GRID FOR CHARTS
# Row 2: Large Analysis Cards

# Pastels for metrics 
pastel_colors = ['#E6E1F9', '#FFE5D9', '#D8F3DC', '#CAF0F8', '#6D597A']

col1, col2= st.columns(2)

with col1:
    st.subheader("Market Trend")
    df = pd.DataFrame({'x': range(10), 'y': [5, 4, 6, 7, 6, 8, 9, 7, 8, 10]})
    fig = px.line(df, x='x', y='y', template="plotly_white")
    # Using the dark muted purple so we can read it
    fig.update_traces(line_color='#6D597A', line_width=3)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader("Allocation")
    fig_pie = px.pie(
        values=[40, 30, 30], 
        names=['BTC', 'ETH', 'Other'], 
        hole=0.7,
        color_discrete_sequence=pastel_colors # forces the chart to be pastel instead of the bright blue and red default
    )
    fig_pie.update_layout(
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_pie, width='stretch')
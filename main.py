import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(layout="wide")

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0, "USDC":0.0, "Other": 0.0}

@st.cache_data(ttl=300) 
def get_data():
    ids = "bitcoin,tether,ethereum,solana,usdc"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"
    response = requests.get(url)
    return response.json()

@st.cache_data(ttl=600) 
def get_historical_btc(coin_id="bitcoin", days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame(columns=['Date', 'Price'])
    
    data = response.json()
    prices = data.get('prices', [])
    df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])
    df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
    return df

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")


def get_fear_n_greed():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    fng = response.json()['data'][0]
    return fng['value'], fng['value_classification']
    


def extract_sol(data):
    sol_data = data.get('solana', {})
    price = sol_data.get('usd', 0)
    change = sol_data.get('usd_24h_change', 0)
    vol = sol_data.get('usd_24h_vol', 0)
    return price, change, vol

def extract_btc(data):
    btc_data = data.get('bitcoin', {})
    vol = btc_data.get('usd_24h_vol', 0)
    change = btc_data.get('usd_24h_change', 0)
    price = btc_data.get('usd', 0)
    return vol, change, price

def update(coin, amount):
    if amount <= 0:
        st.warning("Please enter an amount greater than 0")         # error check to make sure user enters amount greater than 0
        return 
   
    if coin in st.session_state.portfolio:
        st.session_state.portfolio[coin] += amount
    else:
        # This handles cases where the ticker isn't in your initial dictionary
        st.session_state.portfolio["Other"] += amount

fng_val, fng_label = get_fear_n_greed()
data = get_data()

sol_p, sol_c, sol_v = extract_sol(data)
btc_v, btc_c, btc_p = extract_btc(data)

st.title("Crypto Analysis Dashboard")

# The inputs
with st.expander("➕ Add New Asset to Portfolio"):
    input_col1, input_col2, input_col3 = st.columns([2, 2, 1])
    with input_col1:
        coin = st.selectbox("Ticker", ["BTC", "ETH", "SOL", "USDC", "USDT"])
    with input_col2:
        amount = st.number_input("Amount ($)", min_value=0.0)
    with input_col3:
        st.write(" ") 
        # When clicked, this calls our update logic
        if st.button("Update Dashboard"):
            update(coin, amount)
            st.success(f"Added ${amount} to {coin}")

# The Metric Grid
# horizontal block for divs
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Fear & Greed", fng_val, fng_label)
with m2:
    st.metric("BTC Price", f"${btc_p:,.0f}", f"{btc_c:.2f}%")
with m3:
    st.metric("Top Performer (SOL)", f"${sol_p:,.2f}", f"{sol_c:.2f}%")
with m4:
    st.metric("24h Volume", f"${btc_v/1e9:.1f}B", f"{btc_c:.2f}%")


# THE GRID FOR CHARTS
# Row 2: Large Analysis Cards

# Pastels for metrics 
pastel_colors = ['#E6E1F9', '#FFE5D9', '#D8F3DC', '#CAF0F8', '#6D597A']

col1, col2= st.columns(2)

with col1:
    st.subheader("Bitcoin Market Trend")
    
    # Fetch real historical data
    df_trend = get_historical_btc("bitcoin", days=10)
    
    fig = px.line(df_trend, x='Date', y='Price', template="plotly_white")
    
    # Styling to match your bento grid
    fig.update_traces(line_color='#6D597A', line_width=3)
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified" 
    )
    st.plotly_chart(fig, width = 'stretch')
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

# the above handles the button clicks and puts them in session state (how streamlit keeps track of movements)

with col2:
    st.subheader("Allocation")
    
    # Get values and names directly from session state
    portfolio_data = st.session_state.portfolio
    chart_values = list(portfolio_data.values())
    chart_names = list(portfolio_data.keys())

    # Renders chart if data exists 
    if sum(chart_values) > 0:
        fig_pie = px.pie(
            values=chart_values, 
            names=chart_names, 
            hole=0.7,
            color_discrete_sequence=pastel_colors 
        )
        fig_pie.update_layout(
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_pie, width = "stretch")
    else:
        st.info("Please add assets to see the allocation")


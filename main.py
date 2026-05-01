import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards

st.title('Analysis')
st.divider()

col = st.columns([4.45,0.3, 1, 0.2,2]) 

# intialize session state for user input
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = []

if 'pe_score' not in st.session_state:
    st.session_state['pe_score'] = {}

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = set()

data = []
   

# user input in sidebar
with st.sidebar:
    st.title('Portfolio Information 💼')
    st.write('')
    st.divider()
    ticker = st.selectbox('Select a Stock Ticker:', ('AAPL', 'MSFT', 'NVDA', 'GOOG', 'META', 'V', 'WMT', 'ORCL', 'IBM'))
   

    st.write('')
    amount = st.number_input("Amount to invest in the stock")

    if st.button('Add to Portfolio'):
        if ticker == '' or amount <= 0:
            st.error("Please fill in empty fields", icon = '❌')        # makes sure user fills in all fields

        if ticker not in st.session_state['user_input']:
            st.session_state['user_input'].add(ticker)

        for i in st.session_state['user_input']:
            t = yf.Ticker(i)
            d_yield = t.info['dividendYield']
            pe_score = t.info.get('forwardPE', None)

           # this is collecting the data for the dataframe for my scatterplot
            data.append({

                "PE_score": pe_score,
                "Dividend_Yield": d_yield
                 })
            

        

            with col[4]:

                st.metric(label="DivYield for " + i, value=d_yield)
            style_metric_cards(background_color = "#292D34")

            st.markdown("""
            <style>
            [data-testid="metric-container"] {
                width: 100% !important;       
            }
            </style>
        """, unsafe_allow_html=True)



        #st.write(st.session_state['user_input'])

        st.session_state['portfolio'].append({"ticker": ticker, "amount": amount})  # session state for portfolio percent breakdown
        df1 = pd.DataFrame(st.session_state['portfolio'])
        fig1 = px.pie(df1, 
                      values='amount', 
                      names='ticker', 
                      title = 'Portfolio Breakdown',
        )
        col[0].plotly_chart(fig1)

        ratio = yf.Ticker(ticker)
        st.session_state['pe_score'][ticker] = {"pe score": ratio.info['forwardPE']}            # keeps track of the pe score of the stocks the user selects
        df2 = pd.DataFrame.from_dict(st.session_state['pe_score'], orient='index')

        df2.index.name = 'ticker'           
        df2 = df2.reset_index()             # makes sure the index is ticker for x axis
        fig2 = px.bar(df2,                  # pe score chart criteria
                      x='ticker', 
                      y="pe score", 
                      color="ticker", 
                      text_auto=True)

        with col[0]:
            st.plotly_chart(fig2)

    # scatterplot dataframe and plot
    df3 = pd.DataFrame(data)
    if not df3.empty:
        fig3 = px.scatter(df3, x = "PE_score", y = 'Dividend_Yield')

        with col[0]:
            st.plotly_chart(fig3)


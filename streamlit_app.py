import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.title("Stock Price Analysis")

user_input = st.text_input("Enter a Stock Ticker", "SBIN.NS")

start_date = st.date_input("Start Date", value=datetime.today() - timedelta(days=365))
end_date = st.date_input("End Date", value=datetime.today())

ma = ['50 Days', '100 Days', '200 Days']

buffering_indicator = st.empty()

def plot_moving_average(ma_period):
    st.sidebar.subheader(f"Closing Price vs Time Chart with {ma_period} Moving Average")
    hist_data['MA' + str(ma_period)] = hist_data['Close'].rolling(window=ma_period).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], name='Close Price'))
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA' + str(ma_period)], name=f'{ma_period}-Day MA'))
    st.sidebar.plotly_chart(fig)

try:
    ticker_data = yf.Ticker(user_input)
    hist_data = ticker_data.history(start=start_date, end=end_date)

    if hist_data.empty:
        st.error("No data found for given ticker symbol or date range.")
    else:
        st.subheader(f"Stock Price of `{user_input}` *({start_date} to {end_date})*")
        st.write(hist_data.describe())

        st.subheader("Stock Performance")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist_data.index,
                                     open=hist_data['Open'],
                                     high=hist_data['High'],
                                     low=hist_data['Low'],
                                     close=hist_data['Close']))
        fig.update_layout(xaxis_rangeslider_visible=False)

        timeframe = st.radio("Select Timeframe", ('Daily', 'Weekly', 'Monthly'))
        if timeframe == 'Weekly':
            fig.update_layout(xaxis_rangeslider_visible=False, xaxis_rangeslider_range=[hist_data.index[0], hist_data.index[-1]])
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=["thu", "fri"])])
        elif timeframe == 'Monthly':
            fig.update_layout(xaxis_rangeslider_visible=False, xaxis_rangeslider_range=[hist_data.index[0], hist_data.index[-1]])
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=["thu", "fri"])])
            fig.update_xaxes(rangebreaks=[dict(bounds=["2023-12-23", "2024-01-01"])])
        st.plotly_chart(fig)

        st.sidebar.subheader("Moving Average Analysis")
        user_selection = st.sidebar.selectbox("Select the Moving Average Plot", ma)

        if st.sidebar.button("Show"):
            if user_selection == "50 Days":
                plot_moving_average(50)
            elif user_selection == "100 Days":
                plot_moving_average(100)
            elif user_selection == "200 Days":
                plot_moving_average(200)

            # Download Data
            st.sidebar.subheader("Download Data")
            csv = hist_data.to_csv(index=False)
            st.sidebar.download_button(label="Download data as CSV", data=csv, file_name='stock_data.csv', mime='text/csv')

except Exception as e:
    st.error(f"Error fetching data: {e}")
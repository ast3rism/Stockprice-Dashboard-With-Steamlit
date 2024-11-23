# importing required libraries
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# set a title for the app
st.title("Stock Price Analysis")

# take the stock ticker as input from the user
user_input = st.text_input("Enter a Stock Ticker", "SBIN.NS")

# setting the start and end dates to display stock details
start_date = st.date_input("Start Date", value=datetime.today() - timedelta(days=365))
end_date = st.date_input("End Date", value=datetime.today())

# moving average for 50, 100 and 200 days
ma = ['50 Days', '100 Days', '200 Days']

# initialising buffer for less jarring interface
buffering_indicator = st.empty()

# function to plot moving average
def plot_moving_average(ma_period):
    st.sidebar.subheader(f"Closing Price vs Time Chart with {ma_period} Moving Average")
    hist_data['MA' + str(ma_period)] = hist_data['Close'].rolling(window=ma_period).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], name='Close Price'))
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA' + str(ma_period)], name=f'{ma_period}-Day MA'))
    st.sidebar.plotly_chart(fig)

try:
    # loading ticker data from user
    ticker_data = yf.Ticker(user_input)
    hist_data = ticker_data.history(start=start_date, end=end_date)

    # if ticker data is unavailable/incorrect, display appropriate message.
    if hist_data.empty:
        st.error("No data found for given ticker symbol or date range.")
        
    else:
        # display the stock price and other relevant details
        st.subheader(f"Stock Price of `{user_input}` *({start_date} to {end_date})*")
        st.write(hist_data.describe())

        # plot the stock performance if available
        st.subheader("Stock Performance")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist_data.index,
                                     open=hist_data['Open'],
                                     high=hist_data['High'],
                                     low=hist_data['Low'],
                                     close=hist_data['Close']))
        fig.update_layout(xaxis_rangeslider_visible=False)

        # option to select the timeframe to plot
        timeframe = st.radio("Select Timeframe", ('Daily', 'Weekly', 'Monthly'))
        if timeframe == 'Weekly':
            fig.update_layout(xaxis_rangeslider_visible=False, xaxis_rangeslider_range=[hist_data.index[0], hist_data.index[-1]])
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=["thu", "fri"])])
        elif timeframe == 'Monthly':
            fig.update_layout(xaxis_rangeslider_visible=False, xaxis_rangeslider_range=[hist_data.index[0], hist_data.index[-1]])
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=["thu", "fri"])])
            fig.update_xaxes(rangebreaks=[dict(bounds=["2023-12-23", "2024-01-01"])])
        st.plotly_chart(fig)

        #analysis of moving average
        st.sidebar.subheader("Moving Average Analysis")
        user_selection = st.sidebar.selectbox("Select the Moving Average Plot", ma)

        # plotting moving average based on user selection
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

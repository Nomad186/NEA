import math
import tkinter as tk
from tkinter import *
import time
from PIL import ImageTk,Image
import tkinter.font as tkFont
import plotly.graph_objs as go
import requests
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
import praw
import monteCarlo
import BinomialModel
import VAR
import yfinance as yf
from datetime import datetime, timedelta
import fitting_normal

reddit = praw.Reddit(client_id = "Jj0vtWbukCF2RwqTjnLrAg",
                     client_secret = "bp9h30njZU4WZAUxc1U7NagHxOlrLg",
                     username = "Confident_Contract53",
                     password = "22Semaphore?",
                     user_agent = "skibidi"
)

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


analyzer = SentimentIntensityAnalyzer()


root = tk.Tk()
root.title("NMD investment interface")
frame = Frame(root)
PATH_ = "C:\\Users\\Portly\\OneDrive\\Desktop\\NEACS\\NEACS2"

################################################################
#TESTING VALUES
arr = [1, 2, 3, 4, 5, 6, 7,8,9,10,11,12,13,14,15,16,17,18,19]


class GUI:
    def __init__(self):
        self.frame = Frame(root)
        self.frame.pack(side="top",expand=True,fill="both")
        self.API_key = self.get_API_key()
        self.ir_API_key = self.get_ir_API_key()

        settingsFile = open("settings.txt","r")
        self.settings = self.openSettings(settingsFile)

        self.font = tkFont.Font(family=self.settings[0])
        self.name = self.settings[1]


        self.graph_rendered = False

        ico = Image.open("wpk.ico")
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(False, photo)

    def genGraph(self,arr,name):
        trace = go.Scatter(y=arr, mode='lines+markers', name='Float Line')
        layout = go.Layout(title='Price ($)', xaxis=dict(title='Index'), yaxis=dict(title='Value'))
        fig = go.Figure(data=[trace], layout=layout)
        fig.write_image(name + ".png")

    def get_API_key(self):
        file = open("API_key.txt","r")
        contents = file.readlines()[1]
        return contents

    def get_ir_API_key(self):
        file = open("API_key2.txt","r")
        contents = file.readlines()[0]
        return contents

    def get_interest_rate(self):
        api_url = 'https://api.api-ninjas.com/v1/interestrate?country=United Kingdom'
        response = requests.get(api_url, headers={'X-Api-Key': 'drvDCWRwe4/ntjbEeh0VFg==i87z9hpQaFuHt6P0'})
        if response.status_code == requests.codes.ok:
            return (response.json()["central_bank_rates"][0]["rate_pct"])
        else:
            print("Error:", response.status_code, response.text)

    def get_last_two_prices(self, ticker):
        symbol = ticker
        today = datetime.today()

        start_date = today - timedelta(days=7)
        data = yf.download(symbol, start=start_date, end=today)

        last_two_days = data['Close'].tail(2)
        closing_prices = list(last_two_days.values)

        return [closing_prices[0], closing_prices[1]]


    def openSettings(self,text_file):
        contents = text_file.readlines()
        settings = []

        #######FONT#######
        font = contents[1].strip()
        settings.append(font)

        name = contents[3].strip()
        settings.append(name)

        return settings

    def get_daily_closing_prices(self, symbol, api_key):
        # Define the Alpha Vantage API endpoint
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

        # Make the API request
        response = requests.get(url)
        data = response.json()

        # Check if the response contains the expected data
        if 'Time Series (Daily)' not in data:
            raise ValueError("Unexpected response format from Alpha Vantage API")

        # Extract the time series data
        time_series = data['Time Series (Daily)']

        # Extract the last 30 daily closing prices
        closing_prices = []
        for date in sorted(time_series.keys(), reverse=True)[:30]:
            closing_price = time_series[date]['4. close']
            closing_prices.append(float(closing_price))

        print("[TEST] closing prices :", closing_prices[::-1])

        return closing_prices[::-1]

    def get_past_week_closing_prices(self, symbol, api_key):

        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

        response = requests.get(url)
        data = response.json()

        if 'Time Series (Daily)' not in data:
            raise ValueError("Unexpected response format from Alpha Vantage API")

        time_series = data['Time Series (Daily)']

        closing_prices = []
        for date in sorted(time_series.keys(), reverse=True)[:7]:
            closing_price = time_series[date]['4. close']
            closing_prices.append(float(closing_price))

        print("[TEST] closing prices :", closing_prices[::-1])

        return closing_prices[::-1]


    def value_at_risk_button(self, timeSeriesArrs, N , portfolio_weights, num_simulations, show_graph , drift_choice):
        x = VAR.value_at_risk(timeSeriesArrs , dt = 0.01, portfolio_weights = portfolio_weights, num_simulations=num_simulations, show_graph=show_graph , drift_choice=drift_choice, N = N)
        print(x)
        return x

    def show_VAR_result(self,VAR_results,confidence_interval):
        #take bottom p% of end results into a list - then take the largest out of these

        print("hi" , VAR_results)

        mu = fitting_normal.find_mean(VAR_results)
        var = fitting_normal.find_mean(VAR_results)

        fitting_normal.graph_distribution(mu, var)
        CEIL = math.floor(confidence_interval * len(VAR_results)) + 1

        VAR_results.sort()
        lowest_result = VAR_results[CEIL]

        self.frame.result_label = Label(self.frame, text = f"VaR at {confidence_interval} is {lowest_result}",font = self.font, fg = "blue")
        self.frame.result_label.grid(row = 28, column = 1)


    def interpret(self,num):
        if num == 1:
            return True
        return False

    def render_capM_page(self):
        self.clearFrame()

        #######
        var = tk.IntVar()

        self.frame.show_graph_button = tk.Checkbutton(self.frame, text="Show graph?", variable=var,onvalue=1, offvalue=0, font = self.font)
        self.frame.show_graph_button.grid(row = 21, column = 1)

        var2 = tk.IntVar()

        self.frame.drift_choice_button = tk.Checkbutton(self.frame, text = "add drift?" , variable = var2, onvalue = 1, offvalue = 0, font = self.font)
        self.frame.drift_choice_button.grid(row = 23, column = 1)


        #######
        my_portfolio = self.read_my_portfolio()
        folio_weights = [].copy()

        for i in my_portfolio:
            folio_weights.append(int(i[1]))
        #####

        self.frame.welcome_label = Label(self.frame, text = "welcome to the Value at Risk page", font = self.font)
        self.frame.welcome_label.grid(row = 1, column = 1)

        self.frame.return_to_home = Button(self.frame, text = "Return to home", command = self.render_home, font = self.font)
        self.frame.return_to_home.grid(row = 3, column = 1)

        self.frame.advance_label = Label(self.frame, text = "enter the confidence level p: ", font = self.font)
        self.frame.advance_label.grid(row = 7, column = 1)

        self.frame.p_value_entry = Entry(self.frame,font = self.font)
        self.frame.p_value_entry.grid(row = 10, column = 1)

        self.frame.enter_symbol = Entry(self.frame, font = self.font)
        self.frame.return_to_home.grid(row = 5, column = 1)

        self.frame.ask_num_simulations_label = Label(self.frame, text = "enter num simulations: " , font = self.font)
        self.frame.ask_num_simulations_label.grid(row = 13, column = 1)

        self.frame.ask_num_simulations_entry = Entry(self.frame, font = self.font)
        self.frame.ask_num_simulations_entry.grid(row = 15, column = 1)



        #we need to get price data for value at risk

        #####get daily closing prices for each item in 'folio

        time_series_arrs = []

        for record in my_portfolio:
            closing_prices = self.get_daily_closing_prices(record[0] , self.API_key)
            time_series_arrs.append(closing_prices)

        self.frame.go_button = Button(self.frame, text = "go!" , font = self.font, command= lambda: self.show_VAR_result(self.value_at_risk_button(time_series_arrs , num_simulations = int(self.frame.ask_num_simulations_entry.get()) , drift_choice = var2.get(), show_graph=self.interpret(var.get()), portfolio_weights=folio_weights , N = 200) , float(self.frame.p_value_entry.get())))
        self.frame.go_button.grid(row = 26, column = 1)

        #end_returns = VAR.value_at_risk(time_series_arrs , N = self.frame.ask_num_simulations_entry.get() , dt = 0.01 , drift_choice = var2.get() , show_graph=var.get(), portfolio_weights=folio_weights)


    def render_sentiment_analysis_page(self):
        self.clearFrame()

        self.frame.welcome_label = Label(self.frame, text = "welcome to sentiment analysis", font = self.font)
        self.frame.welcome_label.grid(row = 1, column = 1)

        self.frame.return_to_home = Button(self.frame, text = "Return to home", command = self.render_home, font = self.font)
        self.frame.return_to_home.grid(row = 3, column = 1)

        self.frame.prompt_label = Label(self.frame, text = "Enter ticker: ", font = self.font)
        self.frame.prompt_label.grid(row = 6, column = 1)


        self.frame.enter_ticker = Entry(self.frame, font = self.font)
        self.frame.enter_ticker.grid(row = 6, column = 5)

        self.frame.enter_num_posts = Entry(self.frame, font = self.font) 
        self.frame.enter_num_posts.grid(row = 6, column = 8)

        self.frame.go_button = Button(self.frame, text = "go!", font = self.font, command = lambda: self.display_sentiment_result(self.get_sentiment(num_posts = int(self.frame.enter_num_posts.get()) , ticker = self.frame.enter_ticker.get() , subreddit = clicked.get())))
        self.frame.go_button.grid(row = 6, column = 10)
        
        options = ["wallstreetbets",
                   "investing",
                   "StockMarket",
                   "ValueInvesting"]
        
        clicked = StringVar()
        clicked.set('wallstreetbets')

        self.frame.drop = OptionMenu(self.frame,clicked,*options)
        self.frame.drop.grid(row = 11, column = 1)


    def agg(self,list):
        sum = 0
        for i in list:
            sum += i
        return sum

    def mean(self,list):
        if len(list) == 0:
            return "err"
        return self.agg(list) / len(list)

    def variance(self,list):
        if len(list) == 0:
            return "err"
        #SUM OF SQUARES
        SUM_OF_SQUARES = 0

        for i in list:
            SUM_OF_SQUARES += i**2
    
        return (SUM_OF_SQUARES/len(list)) - self.mean(list = list)**2

    def get_sentiment(self,num_posts,ticker,subreddit):
        SUB = reddit.subreddit(subreddit)
        posts = SUB.hot(limit = num_posts)
    
        wanted_posts = []
        sentiment = []

        for submission in posts:
            t_sub_title = word_tokenize(submission.title)
            t_sub_body = word_tokenize(submission.selftext)


            for token in (t_sub_title + t_sub_body):
                if token.upper() == ticker.upper():
                    wanted_posts.append(submission)
        
        ###### DISPLAY POST TITLES

        for post in wanted_posts:
            if post.selftext != "":
                sentiment.append(analyzer.polarity_scores(post.selftext)['compound'])
    
        #print(mean(sentiment))
        #print(variance(sentiment))

        return (self.mean(sentiment), self.variance(sentiment))
    
    def display_sentiment_result(self,res_tuple):
        if res_tuple[0] == "err":
            self.frame.no_post_found_label = Label(self.frame, text = "No posts found.", font = self.font)
            self.frame.no_post_found_label.grid(row = 12, column = 5)

        else:
            self.frame.mean_label = Label(self.frame, text = f"mean : {res_tuple[0]}", font = self.font)
            self.frame.variance_label = Label(self.frame, text = f"variance : {res_tuple[1]}", font = self.font)

            self.frame.mean_label.grid(row = 12, column = 1)
            self.frame.variance_label.grid(row = 12, column = 5)

    def start2(self):
        #interest_rate = self.get_interest_rate()
        root.geometry("651x268")
        interest_rate = "5"

        print(f"geometry : {root.geometry()}")

        self.frame.hello_label = Label(self.frame, text = f"hello, {self.name}" , font = self.font)
        self.frame.hello_label.grid(row = 1, column = 1)

        self.frame.settings_button = Button(self.frame, text = "settings" , font = self.font , command = self.render_settings_page)
        self.frame.settings_button.grid(row = 1, column = 7)

        self.frame.interest_rate_label = Label(self.frame, text = f'Current interest rate: {interest_rate}%', font = self.font, fg = "blue")
        self.frame.interest_rate_label.grid(row = 4, column = 1)

        Sp500 = self.get_last_two_prices("^GSPC")
        NASDAQ = self.get_last_two_prices("^IXIC")
        FTSE100 = self.get_last_two_prices("^FTSE")
        nyse = self.get_last_two_prices("^NYA")
        oil = self.get_last_two_prices("CL=F")
        b_oil = self.get_last_two_prices("BZ=F")
        gold = self.get_last_two_prices("GC=F")
        soycuck = self.get_last_two_prices("ZS=F")

        if Sp500[1] > Sp500[0]:
            self.frame.sp_label = Label(self.frame, text = f"S&P500 : {round(Sp500[1],2)}",fg = "green" , font = self.font)
            self.frame.sp_label.grid(column = 1, row = 9)
        else:
            self.frame.sp_label = Label(self.frame, text = f"S&P500 : {round(Sp500[1],2)}",fg = "red" , font = self.font)
            self.frame.sp_label.grid(column = 1, row = 9)
        ####################################################################################
        if soycuck[1] > soycuck[0]:
            self.frame.soy_label = Label(self.frame, text = f"Soy futures: {round(soycuck[1],2)}",fg = "green", font = self.font)
            self.frame.soy_label.grid(column=7, row = 15)
        else:
            self.frame.soy_label = Label(self.frame, text = f"Soy futures: {round(soycuck[1],2)}",fg = "red", font = self.font)
            self.frame.soy_label.grid(column=7, row = 15)


        ####################################################################################
        if oil[1] > oil[0]:
            self.frame.oil_label = Label(self.frame , text = f"WTI crude oil: {round(oil[1] , 2)}" , fg = "green" , font = self.font)
            self.frame.oil_label.grid(row = 9, column = 7)
        else:
            self.frame.oil_label = Label(self.frame , text = f"WTI crude oil: {round(oil[1] , 2)}" , fg = "red" , font = self.font)
            self.frame.oil_label.grid(row = 9, column = 7)
        ####################################################################################
        if b_oil[1] > b_oil[0]:
            self.frame.boil_label = Label(self.frame , text = f"brent crude oil: {round(b_oil[1] , 2)}" , fg = "green" , font = self.font)
            self.frame.boil_label.grid(row = 11, column = 7)
        else:
            self.frame.boil_label = Label(self.frame , text = f"brent crude oil: {round(b_oil[1] , 2)}" , fg = "red" , font = self.font)
            self.frame.boil_label.grid(row = 11, column = 7)
        #####################################################################################
        if gold[1] > gold[0]:
            self.frame.gold_label = Label(self.frame , text = f"gold: {round(gold[1] , 2)}" , fg = "green" , font = self.font)
            self.frame.gold_label.grid(row = 13, column = 7)
        else:
            self.frame.gold_label = Label(self.frame , text = f"gold: {round(gold[1] , 2)}" , fg = "red" , font = self.font)
            self.frame.gold_label.grid(row = 13, column = 7)




        #####################################################################################

        if NASDAQ[1] > NASDAQ[0]:
            self.frame.nsdq = Label(self.frame, text = f"NASDAQ : {round(NASDAQ[1],2)}" , fg = "green" , font = self.font)
            self.frame.nsdq.grid(column = 1, row = 11)
        else:
            self.frame.nsdq = Label(self.frame, text = f"NASDAQ : {round(NASDAQ[1],2)}" , fg = "red", font = self.font)
            self.frame.nsdq.grid(column = 1, row = 11)

        #####################################################################################

        if FTSE100[1] > FTSE100[0]:
            self.frame.ftse = Label(self.frame, text = f"FTSE100 : {round(FTSE100[1],2)}" , fg = "green" , font = self.font)
            self.frame.ftse.grid(column = 1, row = 13)
        else:
            self.frame.ftse = Label(self.frame, text = f"FTSE100 : {round(FTSE100[1],2)}" , fg = "red" , font = self.font)
            self.frame.ftse.grid(column = 1, row = 13)

        ######################################################################################

        if nyse[1] > nyse[0]:
            self.frame.nyse = Label(self.frame, text = f"NYSE : {round(nyse[1],2)}" , fg = "green" , font = self.font)
            self.frame.nyse.grid(column = 1, row = 15)
        else:
            self.frame.nyse = Label(self.frame, text = f"NYSE : {round(nyse[1],2)}" , fg = "red" , font = self.font)
            self.frame.nyse.grid(column = 1, row = 15)

        #########################################################################

        self.frame.button1 = Button(self.frame , text="Price history" , command = self.render_page1, font = self.font)
        self.frame.button1.grid(row = 17, column = 1)

        self.frame.button_goto_optionPricing = Button(self.frame, text = "go to option pricing", command=self.render_page2, font = self.font)
        self.frame.button_goto_optionPricing.grid(row = 17, column = 4)

        self.frame.button_goto_my_portfolio = Button(self.frame, text = "my portfolio", command = self.render_my_portfolio, font = self.font)
        self.frame.button_goto_my_portfolio.grid(row = 17, column = 7)

        self.frame.capM_button = Button(self.frame, text = "Value - at - Risk", command = self.render_capM_page, font = self.font)
        self.frame.capM_button.grid(row = 20, column = 1)

        self.frame.reddit_sentiment_analysis = Button(self.frame, text = "Reddit sentiment analysis", command = self.render_sentiment_analysis_page, font = self.font)
        self.frame.reddit_sentiment_analysis.grid(row = 20, column = 4)

        self.frame.exit_button = Button(self.frame, text = "exit", command = exit, font = self.font)
        self.frame.exit_button.grid(row = 20, column = 7)


    def change_name(self,new_name):
        f = open("settings.txt","r")
        f_lst = f.readlines()
        f_lst[3] = new_name
        f.close()

        f_w = open("settings.txt","w")
        f_w.writelines(f_lst)
        f.close()

    def render_change_name_entry(self):
        self.frame.new_name_entry = Entry(self.frame, font = self.font)
        self.frame.new_name_entry.grid(row = 5, column = 1)

        self.frame.submit_name_button = Button(self.frame, text = "change", font = self.font , command = lambda : self.change_name(self.frame.new_name_entry.get()))
        self.frame.submit_name_button.grid(row = 5, column = 3)

    def change_font(self, newFont):
        #needs to open settings

        settings_file = open("settings.txt","w")
        settings_list = [line.strip() for line in settings_file.readlines()]

        settings_list[1] = newFont

        settings_file.writelines(settings_list)

        return -1





    def render_settings_page(self):
        self.clearFrame()
        root.geometry("651x268")
        self.frame.welcome_to_settings = Label(self.frame, text = "Settings Page" , font = self.font)
        self.frame.welcome_to_settings.grid(row = 1, column = 1)

        self.frame.return_to_home_button = Button(self.frame, text = "home" , font = self.font , command = self.render_home)
        self.frame.return_to_home_button.grid(row = 2, column = 1)

        self.frame.change_name_button = Button(self.frame, text = "Change name?" , font = self.font, command = self.render_change_name_entry)
        self.frame.change_name_button.grid(row = 3,column = 1)

        self.frame.change_font_button = Button(self.frame, text = "Change font" , font = self.font)
        self.frame.change_font_button.grid(row = 7, column = 2)

        selected_font = StringVar()
        selected_font.set("Arial")

        font_options = ["Calibri","Cambria","Dubai","Microsoft JhengHei","Times New Roman","Myanmar Text"]

        self.frame.dropdown = OptionMenu(self.frame,selected_font,*font_options)
        self.frame.dropdown.grid(row = 7, column = 1)



    def start(self):
        self.frame.label1 = Label(self.frame, text="welcome to the home page", font=self.font)
        self.frame.label1.grid(row = 4, column = 4, padx = 12, pady = 13)

        self.frame.button1 = Button(self.frame , text="go to page 1" , command = self.render_page1, font = self.font)
        self.frame.button1.grid(row = 0, column = 1, padx = 10, pady = 5)

        self.frame.button_goto_optionPricing = Button(self.frame, text = "go to option pricing", command=self.render_page2, font = self.font)
        self.frame.button_goto_optionPricing.grid(row = 10, column = 1, padx = 10, pady = 5)

        self.frame.button_goto_my_portfolio = Button(self.frame, text = "my portfolio", command = self.render_my_portfolio, font = self.font)
        self.frame.button_goto_my_portfolio.grid(row = 16, column = 1, padx = 10, pady = 5)

        self.frame.exit_button = Button(self.frame, text = "exit", command = exit, font = self.font)
        self.frame.exit_button.grid(row = 10, column = 6, padx = 4, pady = 4)

        self.frame.capM_button = Button(self.frame, text = "Value - at - Risk", command = self.render_capM_page, font = self.font)
        self.frame.capM_button.grid(row = 14, column = 6, padx = 4, pady = 4)

        self.frame.reddit_sentiment_analysis = Button(self.frame, text = "Reddit sentiment analysis", command = self.render_sentiment_analysis_page, font = self.font)
        self.frame.reddit_sentiment_analysis.grid(row = 17, column = 4, padx = 4, pady = 4)

        self.frame.go_to_settings = Button(self.frame, text = "Settings" , command = self.render_settings_page, font = self.font)
        self.frame.go_to_settings.grid(row = 1, column = 7)

    def clearFrame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        #self.frame.pack_forget()
    
    def render_home(self):
        self.clearFrame()
        self.start2()
    
    def API_search(self,ticker):
        print("*************************")
        print(f"SEARCHING FOR {ticker}")
        print("************************")

    def get_market_information(self, ticker):
        stock = yf.Ticker(ticker)
        info = stock.info

        earnings_per_share = info.get('epsTrailingTwelveMonths')
        price_to_earnings_ratio = info.get('trailingPE')
        dividend_yield = info.get('dividendYield')

        if dividend_yield is not None:
            dividend_yield = dividend_yield * 100

        return [ticker, earnings_per_share, price_to_earnings_ratio, dividend_yield]

    def render_market_information(self, info):
        self.frame.earnings_per_share_label = Label(self.frame, text = f"earnings per share: {info[1]}" , font = self.font)
        self.frame.price_to_earnings_ratio_label = Label(self.frame, text = f"P/E ratio {info[2]}" , font = self.font)
        self.frame.dividend_yield_label = Label(self.frame, text = f"dividend yield {info[3]}" , font = self.font)
        self.frame.ticker_label = Label(self.frame, text = f"ticker {info[0]}" , font = self.font)

        self.frame.ticker_label.grid(row = 31, column = 8)
        self.frame.price_to_earnings_ratio_label.grid(row=33,column = 8)
        self.frame.earnings_per_share_label.grid(row = 35, column = 8)
        self.frame.dividend_yield_label.grid(row = 38, column = 8)
    
    
    def render_page1(self):
        root.geometry("770x268")

        print(self.get_API_key())
        self.clearFrame()
        self.frame.label3 = Label(self.frame, text = "Display price history", font = self.font)
        self.frame.label3.grid(row = 15, column=15,padx = 4,pady=4)

        self.frame.back_to_home_button = Button(self.frame, text = "return to home", command = self.render_home, font = self.font)
        self.frame.back_to_home_button.grid(row = 18,column = 15, padx = 4, pady = 4)

        #self.frame.render_graph_button = Button(self.frame, text = "display graph", command = lambda: DG.display_graph(PATH_), font = self.font)
        #self.frame.render_graph_button.grid(row = 22, column = 15, padx = 4, pady = 4)

        self.frame.ticker_entry_bar = Entry(self.frame, text = "enter ticker", font = self.font)
        self.frame.ticker_entry_bar.grid(row = 25, column = 15, padx = 4, pady = 4)

        self.frame.go_button = Button(self.frame,font = self.font, text = "Display past 30 days",command = lambda: self.genGraph(self.get_daily_closing_prices(self.frame.ticker_entry_bar.get() , self.API_key) , "skibidi")) # self.frame.ticker_entry_bar.get()
        self.frame.go_button.grid(row = 25, column = 19, padx = 4, pady = 4)

        self.frame.weekly_button = Button(self.frame, font = self.font, text = "Display past week",command = lambda : self.genGraph(self.get_past_week_closing_prices(self.frame.ticker_entry_bar.get() , self.API_key) , "ghgh"))
        self.frame.weekly_button.grid(row = 25, column = 22)

        print(self.frame.ticker_entry_bar.get())
        print(len(self.frame.ticker_entry_bar.get()))
        self.frame.display_mkt_info = Button(self.frame, font = self.font, text = "display mkt info", command = lambda : self.render_market_information(self.get_market_information(self.frame.ticker_entry_bar.get())))
        self.frame.display_mkt_info.grid(row=25, column = 25)
        #####

    def render_page2(self): #option pricing
        self.clearFrame()

        self.frame.header_text = Label(self.frame, text = "Welcome to option pricing!",font = self.font)
        self.frame.header_text.grid(row = 15, column=15,padx = 4,pady=4)

        self.frame.back_to_home_button = Button(self.frame, text = "return to home", command = self.render_home, font = self.font)
        self.frame.back_to_home_button.grid(row = 18,column = 15, padx = 4, pady = 4)

        self.frame.euro_options_pricing = Button(self.frame, text = "Price a European option", command = self.render_euro_options_subpage, font = self.font)
        self.frame.euro_options_pricing.grid(row = 21, column = 15, padx = 4, pady = 4)

        self.frame.american_options_pricing = Button(self.frame, text = "Price an american option",command = self.render_american_options_subpage, font = self.font)
        self.frame.american_options_pricing.grid(row = 24,column = 15,padx =4,pady =4)

    def interpret_drop_menu(self,result):
        if result == "Call":
            return "C"
        elif result == "Put":
            return "P"
        else:
            return "C"
    
    def render_result(self,price , tk_widget):
        tk_widget.grid_forget()
        self.frame.result_display = Label(self.frame,text = f"price: ${price}",font = self.font, fg = "blue")
        self.frame.result_display.grid(row = 50, column = 4)

    def render_euro_options_subpage(self):
        self.clearFrame()

        self.frame.header_text = Label(self.frame, text = "welcome to european options pricing", font = self.font)
        self.frame.header_text.grid(row = 1, column = 4, padx = 4, pady = 4)

        self.frame.return_to_main_options_page = Button(self.frame, text = "return to main page", command = self.render_page2, font = self.font)
        self.frame.return_to_main_options_page.grid(row = 4, column = 4, padx = 4, pady = 4)        

        self.frame.return_to_home = Button(self.frame, text = "Return to Home", font = self.font, command = self.render_home)
        self.frame.return_to_home.grid(row = 7, column = 4, padx = 4, pady = 4)

        self.frame.enter_params_label = Label(self.frame, text = "enter parameters: ", font = self.font)
        self.frame.enter_params_label.grid(row = 10, column = 4, padx = 4, pady = 4)

        self.frame.S0_label = Label(self.frame, text = "S0: ", font = self.font)
        self.frame.S0_label.grid(row = 13, column = 3)

        self.frame.S0_entry = Entry(self.frame,font = self.font, width = 7)
        self.frame.S0_entry.grid(row = 13, column=4)

        self.frame.K_label = Label(self.frame, text = "K: ", font = self.font)
        self.frame.K_label.grid(row = 17, column = 3)

        self.frame.K_entry = Entry(self.frame, font = self.font, width = 7)
        self.frame.K_entry.grid(row = 17, column = 4)

        self.frame.T_label = Label(self.frame, text = "T", font = self.font)
        self.frame.T_label.grid(row = 21, column = 3)

        self.frame.T_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.T_entry.grid(row = 21, column = 4)

        self.frame.vol_label = Label(self.frame, text = "vol: " , font = self.font)
        self.frame.vol_label.grid(row = 25, column = 3)#

        self.frame.vol_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.vol_entry.grid(row = 25, column = 4)

        self.frame.interest_rates_label = Label(self.frame, text = "r:", font = self.font)
        self.frame.interest_rates_label.grid(row = 29, column = 3)

        self.frame.interest_rates_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.interest_rates_entry.grid(row = 29, column = 4)

        self.frame.resolution_label = Label(self.frame, text = "N:" , font = self.font)
        self.frame.resolution_label.grid(row =33, column = 3)

        self.frame.resolution_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.resolution_entry.grid(row = 33, column = 4)

        self.frame.enter_num_paths = Label(self.frame, text = "M:" , font = self.font)
        self.frame.enter_num_paths.grid(row = 37, column = 3)

        self.frame.num_paths_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.num_paths_entry.grid(row = 37, column = 4)

        options = ["Call" , "Put"]

        clicked = StringVar()
        clicked.set("Call")

        self.frame.drop_menu = OptionMenu(self.frame, clicked, *options,font = self.font)
        self.frame.drop_menu.grid(row = 41, column = 4)

        self.frame.option_type = Label(self.frame, text = "type: ", font = self.font)
        self.frame.option_type.grid(row = 41, column = 3)

        self.frame.defined_terms = Label(self.frame, text = "S0 - price today , K - strike price," , font = self.font)
        self.frame.defined_terms2 = Label(self.frame, text = "T - time to maturity (years)" , font = self.font)
        self.frame.defined_terms3 = Label(self.frame, text = "r - interest rate, N - resolution of simulation" , font = self.font)
        self.frame.defined_terms4 = Label(self.frame, text = "vol - volatility of stock , M - number of simulations" , font = self.font)

        self.frame.result_label = Label(self.frame, text = "" , font = self.font)
        self.frame.result_label.grid(row = 50, column = 4)

        self.frame.calculate_button = Button(self.frame, text = "    CALCULATE    ", font = self.font , command = lambda : self.render_result(monteCarlo.price_option(
            S0 = float(self.frame.S0_entry.get()),
            K = float(self.frame.K_entry.get()),
            r = float(self.frame.interest_rates_entry.get()),
            vol = float(self.frame.vol_entry.get()),
            T = float(self.frame.T_entry.get()),
            N = int(self.frame.resolution_entry.get()),
            M = int(self.frame.num_paths_entry.get()),
            opttype = self.interpret_drop_menu(clicked.get()),
            showgraph = True

        ) , self.frame.result_label))
        self.frame.calculate_button.grid(row = 47, column = 4) 

        self.frame.defined_terms.grid(row = 53, column = 4)
        self.frame.defined_terms2.grid(row = 56, column = 4)
        self.frame.defined_terms3.grid(row = 59, column = 4)
        self.frame.defined_terms4.grid(row = 62, column = 4)
    
    def priceOption(self,opptype,S0,K,T,N,M,vol,r):
        if opptype == "C":
            return monteCarlo.price_option(
            S0 = S0,
            K = K,
            r = r,
            vol = vol,
            T = T,
            N = N,
            M = M,
            opttype = "C",
            showgraph = True
        )
        elif opptype == "P":
            return BinomialModel.binomial_price_option(
                S0 = S0,
                K = K,
                r = r,
                vol = vol,
                N = N
            )

    def render_american_options_subpage(self):
        self.clearFrame()

        self.frame.header_text = Label(self.frame, text = "price an american option", font = self.font)
        self.frame.header_text.grid(row = 1, column = 4, padx = 4, pady = 4)

        self.frame.return_to_main_options_page = Button(self.frame, text = "return to main page", command = self.render_page2, font = self.font)
        self.frame.return_to_main_options_page.grid(row = 4, column = 4, padx = 4, pady = 4)

        self.frame.back_to_home_button = Button(self.frame, text = "return to home", command = self.render_home, font = self.font)
        self.frame.back_to_home_button.grid(row = 7,column = 4, padx = 4, pady = 4)

        self.frame.enter_params_label = Label(self.frame, text = "enter parameters: ", font = self.font)
        self.frame.enter_params_label.grid(row = 10, column = 4, padx = 4, pady = 4)

        self.frame.S0_label = Label(self.frame, text = "S0: ", font = self.font)
        self.frame.S0_label.grid(row = 13, column = 3)

        self.frame.S0_entry = Entry(self.frame,font = self.font, width = 7)
        self.frame.S0_entry.grid(row = 13, column=4)

        self.frame.K_label = Label(self.frame, text = "K: ", font = self.font)
        self.frame.K_label.grid(row = 17, column = 3)

        self.frame.K_entry = Entry(self.frame, font = self.font, width = 7)
        self.frame.K_entry.grid(row = 17, column = 4)

        self.frame.T_label = Label(self.frame, text = "T", font = self.font)
        self.frame.T_label.grid(row = 21, column = 3)

        self.frame.T_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.T_entry.grid(row = 21, column = 4)

        self.frame.vol_label = Label(self.frame, text = "vol: " , font = self.font)
        self.frame.vol_label.grid(row = 25, column = 3)#

        self.frame.vol_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.vol_entry.grid(row = 25, column = 4)

        self.frame.interest_rates_label = Label(self.frame, text = "r:", font = self.font)
        self.frame.interest_rates_label.grid(row = 29, column = 3)

        self.frame.interest_rates_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.interest_rates_entry.grid(row = 29, column = 4)

        self.frame.resolution_label = Label(self.frame, text = "N:" , font = self.font)
        self.frame.resolution_label.grid(row =33, column = 3)

        self.frame.resolution_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.resolution_entry.grid(row = 33, column = 4)

        self.frame.enter_num_paths = Label(self.frame, text = "M:" , font = self.font)
        self.frame.enter_num_paths.grid(row = 37, column = 3)

        self.frame.num_paths_entry = Entry(self.frame, font = self.font , width = 7)
        self.frame.num_paths_entry.grid(row = 37, column = 4)

        options = ["Call" , "Put"]

        clicked = StringVar()
        clicked.set("Call")

        self.frame.drop_menu = OptionMenu(self.frame, clicked, *options)
        self.frame.drop_menu.grid(row = 41, column = 4)

        self.frame.option_type = Label(self.frame, text = "type: ", font = self.font)
        self.frame.option_type.grid(row = 41, column = 3)

        self.frame.defined_terms = Label(self.frame, text = "S0 - price today , K - strike price," , font = self.font)
        self.frame.defined_terms2 = Label(self.frame, text = "T - time to maturity (years)" , font = self.font)
        self.frame.defined_terms3 = Label(self.frame, text = "r - interest rate, N - resolution of simulation" , font = self.font)
        self.frame.defined_terms4 = Label(self.frame, text = "vol - volatility of stock , M - number of simulations" , font = self.font)

        self.frame.calculate_button = Button(self.frame, text = "    CALCULATE    ", font = self.font)
        self.frame.calculate_button.grid(row = 47, column = 4)

        self.frame.result_label = Label(self.frame, text = "" , font = self.font)
        self.frame.result_label.grid(row = 50, column = 4)

        self.frame.defined_terms.grid(row = 53, column = 4)
        self.frame.defined_terms2.grid(row = 56, column = 4)
        self.frame.defined_terms3.grid(row = 59, column = 4)
        self.frame.defined_terms4.grid(row = 62, column = 4)

    def add_to_my_portfolio(self,ticker,quantity):
        portfolioFile = open("myPortfolio.txt","a")
        portfolioFile.write("\n")
        portfolioFile.write(ticker)
        portfolioFile.write("\n")
        portfolioFile.write(str(quantity))
    
    def read_my_portfolio(self):
        portfolioFile = open("myPortfolio.txt","r")
        portfolio_contents0 = portfolioFile.readlines()
        portfolio_contents1 = []

        #for line in portfolio_contents0:
            #portfolio_contents1.append(line.strip())
        
        for index in range(0,len(portfolio_contents0) -1,2):

            portfolio_contents1.append([portfolio_contents0[index].strip(), portfolio_contents0[index + 1].strip()])
        
        return portfolio_contents1


    def get_last_price(self,symbol, api_key):
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    
        response = requests.get(url)
        data = response.json()
    
        if 'Time Series (Daily)' not in data:
            raise ValueError("Unexpected response format from Alpha Vantage API")

        time_series = data['Time Series (Daily)']

        most_recent_date = sorted(time_series.keys(), reverse=True)[0]
        closing_price = float(time_series[most_recent_date]['4. close'])

        return closing_price
    
    def render_my_portfolio(self):#
        self.clearFrame()
        self.frame.welcome_text = Label(self.frame, text = "Welcome to your portolio",font = self.font)
        self.frame.welcome_text.grid(row = 15,column = 15, padx = 4, pady = 4)
                                        
        self.frame.back_to_home_button = Button(self.frame, text = "return to home", command = self.render_home, font = self.font)
        self.frame.back_to_home_button.grid(row = 18,column = 15, padx = 4, pady = 4)

        self.frame.add_stock_entry_bar = Entry(self.frame, text = "enter ticker", font = self.font)
        self.frame.add_stock_entry_bar.grid(row = 23, column = 15, padx = 1, pady = 4)

        self.frame.qty_entry_bar = Entry(self.frame, text = "enter qty", font = self.font)
        self.frame.qty_entry_bar.grid(row = 23, column = 16,padx = 1,pady=4)


        self.frame.add_button = Button(self.frame, text = "Add",command = lambda : [self.add_to_my_portfolio(self.frame.add_stock_entry_bar.get(),self.frame.qty_entry_bar.get()) ,str(self.render_my_portfolio())], font = self.font)
        self.frame.add_button.grid(row=23, column = 17, padx = 1, pady = 4)

        

        portfolio_list = self.read_my_portfolio()

        totalPrice = 0

        for i in range(0,len(portfolio_list)):
            #layout = "ticker : {:10}    |   quantity : {:10}    |       price: {}"
 
            currentPrice = self.get_last_price(portfolio_list[i][0], self.API_key)
            totalPrice += currentPrice * int(portfolio_list[i][1])

            self.frame.curr_label = Label(self.frame, text = f"ticker : {portfolio_list[i][0]}      |       quantity : {portfolio_list[i][1]}       |           stock price: {currentPrice}         |           total value : {str(round((currentPrice * int(portfolio_list[i][1])) , 2))}", font = self.font)
            #self.frame.curr_label = Label(self.frame, text = layout.format(portfolio_list[i][0] , portfolio_list[i][1]))
            self.frame.curr_label.grid(row = 32 + 5*i, column = 15, padx = 4, pady = 4)
        

        lowest_label = 28 + 5 * (len(portfolio_list)) 

        self.frame.total_price = Label(self.frame, text = f"Total value : {round(totalPrice , 2)}" , font = self.font)
        self.frame.total_price.grid(row = 28, column = 15, padx = 10, pady = 4)

    
    # def render_my_portfolio(self):#
    #     self.clearFrame()
    #     self.frame.welcome_text = Label(self.frame, text = "Welcome to your portolio",font = self.font)
    #     self.frame.welcome_text.grid(row = 15,column = 15, padx = 4, pady = 4)
                                        
    #     self.frame.back_to_home_button = Button(self.frame, text = "return to home", command = self.render_home, font = self.font)
    #     self.frame.back_to_home_button.grid(row = 18,column = 15, padx = 4, pady = 4)

    #     self.frame.add_stock_entry_bar = Entry(self.frame, text = "enter ticker", font = self.font)
    #     self.frame.add_stock_entry_bar.grid(row = 23, column = 15, padx = 10, pady = 4)

    #     self.frame.qty_entry_bar = Entry(self.frame, text = "enter qty", font = self.font)
    #     self.frame.qty_entry_bar.place(x=260, y=75, width=60, height=20)


    #     self.frame.add_button = Button(self.frame, text = "Add",command = lambda : [self.add_to_my_portfolio(self.frame.add_stock_entry_bar.get(),self.frame.qty_entry_bar.get()) ,self.render_my_portfolio()], font = self.font)
    #     self.frame.add_button.place(x=350, y=75)

    #     portfolio_list = self.read_my_portfolio()

    #     for i in range(0,len(portfolio_list)):
    #         self.frame.curr_label = Label(self.frame, text = f"ticker : {portfolio_list[i][0]}      |       quantity : {portfolio_list[i][1]}", font = self.font)
    #         self.frame.curr_label.grid(row = 28 + 5*i, column = 15, padx = 4, pady = 4)
        
    #     lowest_label = 28 + 5 * (len(portfolio_list)) 







def main(): 
    app = GUI()
    app.start2()
    root.mainloop()


main()

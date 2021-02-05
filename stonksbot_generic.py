# imports
import tweepy
import logging
import time
#import pandas as pd
#from pandas_datareader import data
#import yfinance as yf
import stockquotes

# logger set-up
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# tweet_to_ticker method
def tweet_to_ticker(tweet_body):
    ticker = ''
    # for each char
    #for index in range(0,len(tweet_body)):
    for char in tweet_body:
        # if it's an uppercase letter
        if char.isupper():
            # add character to ticker string
            ticker = ticker + char
    print(ticker)
    return ticker

# check_mentions method
def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    # for all tweets that account is mentioned in
    for tweet in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue

        # save text of tweet as a string
        status = api.get_status(tweet.id)
        tweetString = status.text

        # call tweet_to_ticker and store in new variable
        ticker = tweet_to_ticker(tweetString)

        # try/except getting info from stockquotes
        try:
            stockObject = stockquotes.Stock(ticker)
            stockPrice = stockObject.current_price
            print(stockPrice)
            stockIncrease = stockObject.increase_percent
            print(stockIncrease)

            logger.info(f"Answering to {tweet.user.name}")

            #reply with info and image
            if stockIncrease > 0:
                message = ticker + " is STONKS today! It's currently trading at $" + str(stockPrice) + ", up " + str(stockIncrease) + "% on the day!"
                api.update_status(status=message, in_reply_to_status_id=tweet.id)   # for some reason the 'reply feature isn't working, it just prints a normal tweet
                # still trying to get the image upload to work, using just the text for now
                #api.media_upload(media='stonks.png', status=message, in_reply_to_status_id=tweet.id)
                print('4')
            else:
                message = ticker + " is NOT STONKS today. It's currently trading at $" + str(stockPrice) + ", down " + str(stockIncrease) + "% on the day."
                api.update_status(status=message, in_reply_to_status_id=tweet.id)
                # still trying to get the image upload to work, using just the text for now
                #api.media_upload(media='notstonks.jpg', status=message, in_reply_to_status_id=tweet.id)
        except:
            logger.info(f"Answering to {tweet.user.name}")
            api.update_status(status="Uh oh! I didn't recognize that ticker symbol. Please tweet the ticker in ALL CAPS with no other capital letters in the tweet.", in_reply_to_status_id=tweet.id)
            
    return new_since_id

def main():
    # authenticate credentials
    auth = tweepy.OAuthHandler("CONSUMER_KEY", "CONSUMER_SECRET")
    auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")

    # create API object
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    since_id = 1
    while True:
        since_id = check_mentions(api, since_id)
        logger.info("Waiting...")
        time.sleep(5)

if __name__ == "__main__":
    main()
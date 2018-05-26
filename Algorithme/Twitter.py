from Broker import Id
import tweepy

class twitter(object):
	"""docstring for twitter"""

	def __init__(self):
		super(twitter, self).__init__()
		self.consumer_key = Id.twitter.consumer_key
		self.consumer_secret = Id.twitter.consumer_secret
		self.access_token = Id.twitter.access_token
		self.access_token_secret = Id.twitter.access_token_secret

	def main(self):

		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)

		api = tweepy.API(auth)

		public_tweets = api.home_timeline()
		for tweet in public_tweets:
			print (tweet.text)


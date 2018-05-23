
import rest
import Var
import tweepy

def main(Date1, Date2):
	rest.backtest().Pull(Date1, Date2)

	pass


class traitement:
	donnee = "salut"

	def __init__(self):
		self.donnee = "aurevoir"
		print(self.donnee)

class twitter(object):
	"""docstring for twitter"""

	def __init__(self):
		super(twitter, self).__init__()
		self.consumer_key = 'XSJqHueeQbfnRaxwxsBORuVtn'
		self.consumer_secret = "olIFuTKNbMKW3U0VyxcEbtCl9f9MOKh9jHXaZKCxLLUlAbowaO"
		self.access_token = "1634423462-HClnsSDXIDArSMHnNuLJv48aCw219Uis1OyXSWn"
		self.access_token_secret = "Cn8UZRz1ALZlcZqiN0t6cGsMfzgVrVprYlYUugREE0a57"

	def main(self):

		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)

		api = tweepy.API(auth)

		public_tweets = api.home_timeline()
		for tweet in public_tweets:
			print (tweet.text)


if __name__ == '__main__':
	main(Var.D1, Var.D2)

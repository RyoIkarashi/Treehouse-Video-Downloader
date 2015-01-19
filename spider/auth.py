from requests import Session
from lxml import html

class AuthSession(object):
	"""Creates an authenticated session to teamtreehouse.com"""
	SIGNIN_URL = "https://teamtreehouse.com/signin"
	LOGIN_POST_URL = "https://teamtreehouse.com/person_session"

	def __init__(self, user_name, password):
		self.user_name = user_name
		self.password = password
		# set some slightly more 'human' headers
		self.headers = {
			'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
			'Origin': "https://teamtreehouse.com",
			'Referer':"https://teamtreehouse.com/signin",
		}
		# log in data we need to post later
		self.payload = {
			'user_session[email]': self.user_name,
			'user_session[password]': self.password
		}
		# user's session
		self.session = Session()
		self.session.headers.update(self.headers)


	def get_auth_token(self):
		"""parses an authentication from the login form on /signin"""
		response = self.get(self.SIGNIN_URL)

		if response:
			tree = html.fromstring(response.text)
			self.payload['authenticity_token'] = tree.xpath("//form[@id='new_user_session']//input[@name='authenticity_token']/@value")[0]
			return True
		return False


	def login(self):
		""" posts the user's login details, if successful returns session"""
		response = self.session.post(self.LOGIN_POST_URL, data=self.payload)

		if response.status_code == 200:
			tree = html.fromstring(response.text)
			title = tree.xpath("//title/text()")[0]

			if title == "Treehouse | Home":
				return True
		return False


	def authenticate(self):
		""" Grabs token and attempts to login"""
		success = self.get_auth_token()
		
		if success == True:
			return self.login()
		return False


	def get(self, url):
		response = self.session.get(url)

		if response.status_code == 200:
			return response
		else:
			print "Response Code: {0} when trying to fetch {1}".format(response.status_code, url)
		return False
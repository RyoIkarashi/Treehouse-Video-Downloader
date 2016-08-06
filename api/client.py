from requests import Session

def json_response(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)

        if res.status_code == 200:
            return res.json()
        return False
    return wrapper

class TreeHouseAPI:
    CLIENT_ID = "c434aed39dcf1408ddd22b8fc5b3ae7e4cb75da79fa6f31bfba0c9dbf95ecf61"
    CLIENT_SECRET = "b76d64fc82092dcc248026913c0730a0a06bafb807600137ebc94a303ebff1ad"
    AUTH_ENDPOINT = "https://teamtreehouse.com/oauth/token"
    BASE_URL = "https://api.teamtreehouse.com/api/"

    def __init__(self):
        self.session = Session()
        headers = {
            "Accept": "application/vnd.treehouse.v1",
            "User-Agent": "Treehouse Android/53 - Dalvik/2.1.0 (Linux; U; Android 6.0.1; XT1562 Build/MPD24.107-52)",
            "Host": "api.teamtreehouse.com"
        }
        self.session.headers.update(headers)

    def login(self, username, password):
        
        """ authenticates with teamtreehouse's api"""

        payload = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }

        res = self.session.post(self.AUTH_ENDPOINT, data=payload)

        if res.status_code == 200:
            token_header = self._parse_token(res.json())
            self.session.headers.update(token_header)
            return True
        return False

    @json_response
    def get_syllabi(self):
        return self.session.get(self._build_endpoint('syllabi'))

    @json_response
    def get_syllabi_by_id(self, id):
        return self.session.get(self._build_endpoint('syllabi/{0}'.format(id)))

    @json_response
    def get_tracks(self):
        return self.session.get(self._build_endpoint('tracks'))

    @json_response
    def get_topics(self):
        return self.session.get(self._build_endpoint('topics'))

    @json_response
    def get_workshops(self):
        return self.session.get(self._build_endpoint('workshops'))

    @json_response
    def get_video(self, id):
        return self.session.get(self._build_endpoint('videos/{0}'.format(id)))

    def _build_endpoint(self, endpoint):
        return self.BASE_URL + endpoint

    def _parse_token(self, json_token):
        return {"Authorization": "Bearer " + json_token['access_token']}

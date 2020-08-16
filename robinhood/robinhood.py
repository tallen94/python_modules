import requests
import sys
import json

class Robinhood:
    BASE_URL = "https://api.robinhood.com/"
    DEFAULT_HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
        "Content-Type": "application/json; charset=utf-8",
        "X-Robinhood-API-Version": "1.0.0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0",
        "Origin": "https://robinhood.com"
    }
    
    def __init__(self):
        self.base_url = "https://api.robinhood.com"
        self.intervals = [
            ('5minute', 'day'),
            ('10minute', 'day'),
            ('5minute', 'week'),
            ('10minute', 'week'),
            ('day', 'year'),
            ('week', '5year')
        ] 
        
        self.commands = {
            "quotes_hist": self.quotes_hist,
            "quotes": self.quotes,
            "login": self.login,
            "get_symbols": self.get_symbols,
            "get_symbol": self.get_symbol,
            "user": self.user,
            "investment_profile": self.investment_profile,
            "positions": self.positions,
            "get_current_positions": self.get_current_positions,
            "user_id": self.user_id,
            "portfolios": self.portfolios,
            "new_on_robinhood": self.new_on_robinhood
        }
        
    def run_command(self, name, args):
        return self.commands[name](args)
    
    def login(self, args):
        url = "oauth2/token/"
        body = {
            'password': args["password"],
            'username': args["username"],
            'scope': 'internal',
            'grant_type': 'password',
            'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
            'expires_in': 86400,
            'device_token': '4ba299fb-0fa3-4551-bb9c-04fefa415307'
        }
        return self.post(url, body).json()

    def get_symbols(self, args):
        symbols = args["symbols"]
        url = "marketdata/fundamentals/?symbols=" + ",".join(symbols)
        symbols = self.auth_get(url, args["token"]).json()['results']
        return symbols

    def get_symbol(self, args):
        symbol = args["symbol"]
        url = "marketdata/fundamentals/" + symbol + "/"
        symboljson = self.auth_get(url, args["token"]).json()
        symboljson['symbol'] = args["symbol"]
        return symboljson

    def quotes(self, args):
        url = "quotes/" + args["symbol"] + "/"
        return self.get(url).json()

    def quotes_hist(self, args):
        symbol = args["symbol"]
        interval = args["interval"]
        url = "quotes/historicals/" + symbol \
        + "/?" \
        + "interval=" + self.intervals[interval][0] + "&" \
        + "span=" + self.intervals[interval][1]
        return self.get(url).json()['historicals']

    def user(self, args):
        token = args['token']
        url = "user/"
        return self.auth_get(url, token).json()

    def investment_profile(self, args):
        token = args['token']
        url = "user/investment_profile"
        return self.auth_get(url, token).json()

    def positions(self, args):
        token = args["token"]
        url = "positions/"
        return self.auth_get(url, token).json()

    def get_current_positions(self, args):
        p = self.positions(args)["results"]
        filtered = list(filter(lambda x: float(x["quantity"]) > 0, p))
        return self.hydrate_list_values(filtered, 'instrument')

    def hydrate_list_values(self, l, field):
        for item in l:
            item[field] = self.raw_get(item[field]).json()
        return l
    
    def hydrate_list(self, l):
        ret = []
        for item in l:
            ret.append(self.raw_get(item).json())
        return ret

    def new_on_robinhood(self, args):
        url = "midlands/tags/tag/new-on-robinhood/"
        instruments = self.get(url).json()["instruments"]
        return self.hydrate_list(instruments)

    def user_id(self, args):
        token = args["token"]
        url = "user/id/"
        return self.auth_get(url, token).json()

    def portfolios(self, args):
        token = args["token"]
        url = "portfolios/"
        return self.auth_get(url, token).json()

    def auth_post(self, url, token, body, headers = DEFAULT_HEADERS):
        headers['authorization'] = 'Bearer ' + token
        return self.post(url, body, headers)

    def auth_get(self, url, token, headers = DEFAULT_HEADERS):
        headers['authorization'] = 'Bearer ' + token
        return self.get(url, headers)
    
    def raw_auth_get(self, url, token, headers = DEFAULT_HEADERS):
        headers['authorization'] = 'Bearer ' + token
        return self.raw_get(url, headers)
    
    def post(self, url, body, headers = DEFAULT_HEADERS):
        return requests.post(self.BASE_URL + url, data=json.dumps(body), headers=headers)
    
    def get(self, url, headers = DEFAULT_HEADERS):
        return requests.get(self.BASE_URL + url, headers=headers)
    
    def raw_get(self, url, headers = DEFAULT_HEADERS):
        return requests.get(url, headers=headers)

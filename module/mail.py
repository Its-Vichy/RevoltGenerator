import httpx, random, string

class TempMail:
    def __init__(self, proxy: str= None):
        self.session = httpx.Client(headers={'content-type': 'application/json'}, timeout=15, proxies=proxy)
        self.base_url = 'https://api.mail.gw'
    
    def get_domain(self):
        return self.session.get(f'{self.base_url}/domains').json()['hydra:member'][0]['domain']

    def get_mail(self):
        mail = ''.join(random.choice(string.ascii_lowercase) for _ in range(15)) + '@' + self.get_domain()
        response = self.session.post(f'{self.base_url}/accounts', json={'address': mail, 'password': mail}).status_code
        
        if response == 201:
            token = self.session.post(f'{self.base_url}/token', json={'address': mail, 'password': mail}).json()['token']
            self.session.headers['authorization'] = f'Bearer {token}'
            return mail
        else:
            return None
    
    def get_messages(self):
        response = self.session.get(f'{self.base_url}/messages').json()['hydra:member']
        return response
    
    def get_message_content(self, message_id: str):
        response = self.session.get(f'{self.base_url}/messages/{message_id}').json()['text']
        return response
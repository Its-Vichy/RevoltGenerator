import time, threading, random, string, httpx, itertools, os
from colorama import Fore, init; init()
from module import mail, captcha

__proxy__, __invite__, __lock__ = itertools.cycle(open('./data/proxies.txt', 'r+').read().splitlines()), '19HGFnBR', threading.Lock()

class Console:
    @staticmethod
    def printf(content: str):
        __lock__.acquire()
        print(content + Fore.RESET)
        __lock__.release()

class GeneratorThread(threading.Thread):
    def __init__(self):
        self.temp_mail = mail.TempMail('http://' + next(__proxy__))
        self.email = self.temp_mail.get_mail()
        self.password = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

        self.session = httpx.Client(headers={'content-type': 'application/json'}, timeout=15, proxies='http://' + next(__proxy__))

        threading.Thread.__init__(self)

    def get_verification_url(self):
        while True:
            for mess in self.temp_mail.get_messages():
                if mess['from']['address'] == 'noreply@revolt.chat':
                    content = self.temp_mail.get_message_content(mess['id'])
                    url = str('https://app.revolt.chat/login/verify/' + content.split('https://app.revolt.chat/login/verify/')[1][:33]).strip()
                    return url

            time.sleep(5)

    def create_account(self, captcha_key: str):
        response = self.session.post('https://api.revolt.chat/auth/account/create', json={'email': self.email, 'password': self.password, 'captcha': captcha_key}).status_code

        if response == 204:
            return True
        else:
            return False

    def solve_captcha(self):
        while True:
            captcha_key = captcha.solve(next(__proxy__))

            if captcha_key != None:
                return captcha_key

    def get_token(self):
        r = self.session.post("https://api.revolt.chat/auth/session/login", json={"email": self.email,"password": self.password,"captcha": self.solve_captcha(),"friendly_name":"chrome on Windows 10"})

        if r.status_code == 200:
            return r.json()['token']

    def complete(self):
        self.session.post('https://api.revolt.chat/onboard/complete', json={'username': ''.join(random.choice(string.ascii_lowercase) for _ in range(15))})

    def join_server(self):
        self.session.post(f'https://api.revolt.chat/invites/{__invite__}')

    def run(self):
        captcha_key = self.solve_captcha()

        if self.create_account(captcha_key):
            print(f'{Fore.YELLOW}[*] Submit combo -> {self.email}:{self.password}')
            url = self.get_verification_url()
            Console.printf(f'{Fore.CYAN}[>] Verification url -> {url}')
            httpx.post(url)

            token = self.get_token()
            self.session.headers['x-session-token'] = token
            Console.printf(f'{Fore.GREEN}[+] {token}')
            self.complete()
            self.join_server()

            with open('./data/account.txt', 'a+') as f:
                f.write(f'{self.email}:{self.password}:{token}\n')


if __name__ == '__main__':
    os.system('cls')

    while True:
        if threading.active_count() >= 100:
            time.sleep(1)

        GeneratorThread().start()
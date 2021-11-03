import subprocess, time, socks, socket, requests, stem, bs4
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def WebDriver(CHROMEDRIVER_PATH, headless=False):
    options = Options()
    if headless: 
        options.headless = True
    prefs = {
        'download.prompt_for_download': False,
         'download.directory_upgrade': True,
         'safebrowsing.enabled': False,
         'safebrowsing.disable_download_protection': True
    }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(CHROMEDRIVER_PATH,options=options)
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    return driver


class NET():
    
    def __init__(self, tor= False, agent=None, accept=None):
        self.options = {
            'waitingSeconds' : 10,
            'attempts' : 5,
            'torPath' : r'C:/Users/pietr/Documents/Tor Browser/Browser/firefox.exe'
        }
        self.options['UserAgent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0" if agent == None else agent
        self.options['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" if accept == None else accept
        self.options['Proxies'] =  {
            'http':  'socks5://127.0.0.1:9150',
            'https': 'socks5://127.0.0.1:9150'
        } if tor else None
        self.options['Headers'] = {
            "User-Agent": self.options['UserAgent'],
            "Accept": self.options['Accept']
        }
        if tor:
            self.activateTor()
        
    
    def activateTor(self,):
        sproc = subprocess.Popen(self.options['torPath'])
        time.sleep(15)
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
        socket.socket = socks.socksocket
        return None
        
    
    @staticmethod
    def getlxml(response):
        return bs4.BeautifulSoup(
            response.text, 
            'lxml'
        )
    
    
    @staticmethod
    def checkIp():
        ip = requests.get(
            url= "http://www.icanhazip.com", 
            headers= {
                "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
            },
        ).text.split('\n')[0]
        print(f"[NET] Connection moved to Ip: {ip}.")
    
    
    def switchIp(self):
        if self.options['Proxies']:
            socks.setdefaultproxy()
            with Controller.from_port(port=9151) as controller:
                controller.authenticate()
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
                socket.socket = socks.socksocket
                controller.signal(Signal.NEWNYM)
            self.checkIp()
        else:
            raise ValueError("[NET] Tor Connection never initializated.")
    
    
    def reqResponse(self, url, wait=False, lxml=False):
        response = requests.get(
            url=url, 
            headers=self.options['Headers'],
            proxies=self.options['Proxies']
        )
        if not response.ok:
            if wait:
                for _ in range(self.options['attempts']):
                    time.sleep(self.options['waitingSeconds'])
                    response = requests.get(
                        url=url, 
                        headers=self.options['Headers'],
                        proxies=self.options['Proxies']
                    )
                    if response.ok:
                        return response
                if self.options['Proxies']:
                    self.switchIp()
                    to_be_finished
                else:
                    raise ValueError(f"[NET] Maximum attemps reached for {url}.")
            else:
                raise ValueError(f"[NET] No Response with error code: {response.status_code}")
        else:
            return response
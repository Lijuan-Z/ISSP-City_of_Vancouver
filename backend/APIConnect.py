from hugchat import hugchat
from hugchat.login import Login
from config import EMAIL, PASSWD
from config import GOOGLE_API_KEY
import google.generativeai as genai

class APIConnect:
    def __init__(self):
        self.gemini_model = "gemini-1.5-flash-latest"
    @staticmethod
    def hugchat_connect():
        cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
        sign = Login(EMAIL, PASSWD)
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
        # Create ChatBot
        return hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

    @staticmethod
    def hugchat_connect_section():
        cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
        sign = Login(EMAIL, PASSWD)
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
        # Create ChatBot
        return hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

    def gemini_connect(self, system_definition):
        genai.configure(api_key=GOOGLE_API_KEY)
        return genai.GenerativeModel(self.gemini_model, system_instruction=system_definition)
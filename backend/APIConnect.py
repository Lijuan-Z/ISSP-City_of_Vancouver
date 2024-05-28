from hugchat import hugchat
from hugchat.login import Login
from config import EMAIL, PASSWD
from config import GOOGLE_API_KEY
import google.generativeai as genai
import time
import configparser

config = configparser.ConfigParser()
config.read('credential.ini')

class APIConnect:
    """
    A class to handle connections to different APIs such as HugChat and Gemini.
    """

    @staticmethod
    def hugchat_connect():
        """
        Connect to HugChat using predefined user credentials.

        Returns:
            hugchat.ChatBot: An instance of the HugChat bot initialized with user cookies.
        """
        cookie_path_dir = "./cookies/"  # Directory where cookies will be saved; trailing slash is required
        sign = Login(config.get('hf1', 'name'), config.get('hf1', 'password'))  # Login instance created with user credentials
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)  # Perform login and save cookies
        # Create and return ChatBot instance with the obtained cookies
        return hugchat.ChatBot(cookies=cookies.get_dict())  # or use cookie_path="usercookies/<email>.json"

    @staticmethod
    def hugchat_connect_section(max_retries = 3):
        """
        Connect to a specific section of HugChat using predefined user credentials.

        This method is currently identical to hugchat_connect but will be modified in the future
        to handle different user credentials or sections.
        Args:
            max_retries: Maximum number of retries before giving up. Default is 3

        Returns:
            hugchat.ChatBot: An instance of the HugChat bot initialized with user cookies.
        """
        attempts = 0
        while attempts < max_retries:
            try:
                cookie_path_dir = "./cookies/"  # Directory where cookies will be saved; trailing slash is required
                sign = Login(config.get('hf2', 'name'), config.get('hf2', 'password'))  # Login instance created with user credentials
                cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)  # Perform login and save cookies
                # Create and return ChatBot instance with the obtained cookies
                return hugchat.ChatBot(cookies=cookies.get_dict())  # or use cookie_path="usercookies/<email>.json"
            except:
                attempts += 1
                time.sleep(2)
                return None


    @staticmethod
    def gemini_connect(system_definition):
        """
        Connect to the Gemini AI model using a system definition and an API key.

        Args:
            system_definition (str): Instructions or configuration for the Gemini model.

        Returns:
            genai.GenerativeModel: An instance of the Gemini generative model configured with the system definition.
        """
        gemini_model = "gemini-1.5-flash-latest"  # Specify the version of the Gemini model
        genai.configure(api_key=config.get('gemini', 'key'))  # Configure the genai module with the Google API key
        # Create and return an instance of the Gemini generative model with the provided system definition
        return genai.GenerativeModel(gemini_model, system_instruction=system_definition)

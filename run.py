from twitch import Application
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    app = Application()
    app.run()
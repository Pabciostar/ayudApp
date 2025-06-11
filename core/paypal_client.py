import os
from dotenv import load_dotenv
import paypalrestsdk

load_dotenv()

class PayPalClient:
    def __init__(self):
        self.mode = os.getenv('PAYPAL_MODE', 'sandbox')
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET')

        print(f"Modo PayPal: {self.mode}")  # ✅ AQUÍ ESTÁ BIEN

        self.configure()
    
    def configure(self):
        paypalrestsdk.configure({
            "mode": self.mode,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
    
    def get_paypal_client(self):
        return paypalrestsdk
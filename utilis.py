from passlib.context import CryptContext
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

pwd_content = CryptContext(schemes=['bcrypt'],deprecated="auto")

def hash_password(password:str)-> str:
  return pwd_content.hash(password)
print(hash_password,":running")

def verify_password(plain_password:str, hashed_password:str)-> bool:
  return pwd_content.verify(plain_password,hashed_password)
print(verify_password,":verifying")

otp_store = {}

def generate_otp() -> str:
    return str(random.randint(1000, 9999))

def store_otp(email: str, otp: str):
    otp_store[email] = {
        'otp': otp,
        'expires_at': datetime.now() + timedelta(minutes=30)
    }
    print(f"Stored OTP for {email}: {otp}")

def validate_otp(email: str, otp: str) -> bool:
    if email not in otp_store:
        print(f"Email not found in OTP store: {email}")
        return False
    otp_info = otp_store[email]
    if datetime.now() > otp_info['expires_at']:
        print(f"OTP expired for {email}")
        return False
    return otp == otp_info['otp']


def send_email(to_email: str, otp: str):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = 'sisodiya.anjali001@gmail.com'
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('sisodiya.anjali001@gmail.com', 'wxsj zkan jjzl rxlo')
        server.send_message(msg)
        
def send_welcome_email(to_email: str, first_name: str):
    subject = 'Welcome to Our Service!'
    body = f"Hi {first_name},\n\nThank you for signing up! We're excited to have you on board.\n\nBest regards,\nThe Team"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'sisodiya.anjali001@gmail.com'
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('sisodiya.anjali001@gmail.com', 'wxsj zkan jjzl rxlo')
        server.send_message(msg)


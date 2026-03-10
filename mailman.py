import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_pdf_email(recipient_email: str, pdf_path: str, html_content: str):
    if not recipient_email:
        print(".....No recipient email address provided. Skipping.")
        return

    # --- Setup your credentials ---
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    # 1. CRITICAL FIX: Create a brand new message INSIDE the function
    # This guarantees a fresh envelope for every single customer loop.
    msg = EmailMessage()
    msg['Subject'] = "Your Personalized Travel Itinerary is Here!"
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    # 2. Add the plain text fallback FIRST
    msg.set_content("Please enable HTML to view your travel quotation.")
    
    # 3. Add the beautiful HTML body SECOND
    msg.add_alternative(html_content, subtype='html')

    # 4. Add the PDF attachment THIRD
    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            pdf_name = os.path.basename(pdf_path)
            
        msg.add_attachment(
            pdf_data, 
            maintype='application', 
            subtype='pdf', 
            filename=pdf_name
        )
        
        # 5. Connect and Send!
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            
        print(f":::::HTML Email successfully sent to {recipient_email}!")
        
    except Exception as e:
        print(f"X--X Failed to send email to {recipient_email}. Error: {e}")
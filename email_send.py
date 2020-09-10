import os, smtplib, ssl

class Email:
    def __init__(self, receiver_email, supply, qty, pin):
        self.receiver_email = receiver_email # This is the email address that receives emails
        self.supply = supply
        self.qty = qty
        self.pin = pin

    def email_send(self):
        sender_email = os.environ["EMAIL"]
        smtp_server = "smtp.gmail.com"
        port = 587
        password = os.environ["EMAILPASSWORD"]

        subject = "Your Request Has Been approved!"
        text = f'Your request of {self.qty} {self.supply} has been approved! Your pin to sign your item back in is {self.pin}'
        message = f'Subject: {subject}\n\n{text}'

        context = ssl._create_unverified_context()

        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, self.receiver_email, message)
        except Exception as e:
            print(e)
        finally:
            server.quit()

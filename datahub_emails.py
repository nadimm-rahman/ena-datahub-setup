#!/usr/bin/python3

# This script contains class objects and functions involved in preparing and sending emails as part of data hubs set up.

__author__ = 'Nadim Rahman'

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass
from utils import Utilities


class PrepareEmails:
    """ Prepare the email(s) to be sent."""

    def __init__(self, contact_info):
        """
        Initialisation of class
        :param contact_info: Dictionary of contact information for data providers and consumers
        """
        self.contact_info = contact_info
        self.message = MIMEMultipart("alternate")       # Initiating message object to be sent


    def obtain_all_emails(self):
        """
        Obtain all emails from a dictionary of contact information
        :return: List of unique email addresses
        """
        self.emails = []
        for type in self.contact_info.values():
            sheet_emails = list(type['Email'].values())     # List of all emails within a particular sheet
            for sheet_email in sheet_emails:
                if sheet_email not in self.emails:      # Add the email to the list if it doesn't already exist
                    self.emails.append(sheet_email)


    def datahub_credentials(self):
        """
        Adding to message object for data hub credentials email
        :return: Message object to send data hub credentials with
        """
        self.message['Subject'] = "[ENA Data Hubs] Credentials"
        text = """\
Username: []
Password: []
        
European Nucleotide Archive (ENA)
EMBL-EBI"""
        html = """\
            <html>
                <body>
                    <p>Username: []<br>
                    Password: []</p><br>
                    <p style="font-size:12px; font-color:#6b6b6b"><a href="https://www.ebi.ac.uk/ena/browser/home">European Nucleotide Archive (ENA)</a><br>
                    EMBL-EBI</p>
                </body>
            </html>"""

        # Turn these into plain/html MIMEText objects
        plainemail = MIMEText(text, "plain")
        htmlemail = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        self.message.attach(plainemail)
        self.message.attach(htmlemail)


    def prepare_email(self):
        """
        Function runner to obtain a cleaned list of email addresses and message object
        :return:
        """
        self.obtain_all_emails()
        self.datahub_credentials()
        return self.emails, self.message


class SendEmails:
    """Send email(s) that have been prepared."""

    def __init__(self, emails, message, sender_email, port):
        """
        Initialisation of class
        :param emails: List of email addresses
        :param message: Message object for email
        :param sender_email: The admin sender email address
        :param port: Port number to send email
        """
        self.emails = emails
        self.message = message
        self.sender_email = sender_email
        self.port = port


    def send_email(self):
        """
        Send email using initialised parameters
        """
        self.message["From"] = self.sender_email

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        password = getpass()

        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=context) as server:
            server.login(self.sender_email, password)
            for email in self.emails:
                self.message["To"] = email
                server.sendmail(
                    self.sender_email, email, self.message.as_string()
                )



def emailer(args, configuration):
    consumers_providers = Utilities.read_spreadsheet(args.spreadsheet)      # Read in the consumers and providers

    # Prepare the email message and obtain a list of contacts to send the email to
    email_prep = PrepareEmails(consumers_providers)
    emails, message = email_prep.prepare_email()

    # Send the email message
    email_send = SendEmails(emails, message, configuration['ADMIN_EMAIL'], configuration['PORT'])
    email_send.send_email()

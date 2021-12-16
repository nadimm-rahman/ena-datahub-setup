#!/usr/bin/python3

# This script contains class objects and functions involved in preparing and sending emails as part of data hubs set up.

__author__ = 'Nadim Rahman'

import argparse, getpass, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass
from utils import Config, Utilities


def get_args():
    """
    Handle script arguments
    :return: Script arguments
    """
    parser = argparse.ArgumentParser(prog='main.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + =========================================================== +
        |  ENA Data Hubs Setup: main.py                               |
        |  Python tool to handle assignment and set up of a data      |
        |  hub.                                                       |
        + =========================================================== +
        """)
    parser.add_argument('-s', '--spreadsheet', help='Input spreadsheet for the data hub assignment', type=str, required=True)
    parser.add_argument('-d', '--datahub_name', help='Name of data hub to be assigned', type=str, required=True)
    parser.add_argument('-p', '--datahub_password', help='Password for data hub to be assigned', type=str, required=True)
    args = parser.parse_args()
    return args


class PrepareEmails:
    """ Prepare the email(s) to be sent."""

    def __init__(self, contact_info, datahub_name, datahub_password):
        """
        Initialisation of class
        :param contact_info: Dictionary of contact information for data providers and consumers
        """
        self.contact_info = contact_info
        self.dh = datahub_name
        self.pw = datahub_password
        self.message = MIMEMultipart("alternate")  # Initiating message object to be sent

    def obtain_all_emails(self):
        """
        Obtain all emails from a dictionary of contact information
        :return: List of unique email addresses
        """
        self.emails = []
        for sheet in self.contact_info.values():
            try:
                sheet_emails = list(sheet['Email'].values())  # List of all emails within a particular sheet
            except KeyError:
                continue        # If the sheet doesn't contain an 'Email' field, then skip
            for sheet_email in sheet_emails:
                if sheet_email not in self.emails:  # Add the email to the list if it doesn't already exist
                    self.emails.append(sheet_email)

    def datahub_credentials(self):
        """
        Adding to message object for data hub credentials email
        :return: Message object to send data hub credentials with
        """
        self.message['Subject'] = "[ENA Data Hubs] {}: Credentials".format(self.dh)
        text = """\
Username: {}
Password: {}

Please keep these credentials safe and do NOT share with others.
European Nucleotide Archive (ENA)
EMBL-EBI""".format(self.dh, self.pw)
        html = """\
            <html>
                <body>
                    <p>Username: {}<br>
                    Password: {}</p><br>
                    <i><p style="font-size:12px; font-color"#6b6b6b">Please keep these credentials safe and do <b>NOT</b> share with others.</p>
                    <p style="font-size:12px; font-color:#6b6b6b"><a href="https://www.ebi.ac.uk/ena/browser/home">European Nucleotide Archive (ENA)</a><br>
                    EMBL-EBI</p></i>
                </body>
            </html>""".format(self.dh, self.pw)

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
        password = getpass('Email client password: ')

        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=context) as server:
            server.login(self.sender_email, password)
            for email in self.emails:
                self.message["To"] = email
                server.sendmail(
                    self.sender_email, email, self.message.as_string()
                )


if __name__ == '__main__':
    args = get_args()
    configuration = Config.read_config()

    setup_spreadsheet = Utilities.read_spreadsheet(args.spreadsheet)

    email_prep = PrepareEmails(setup_spreadsheet, args.datahub_name, args.datahub_password)
    emails, message = email_prep.prepare_email()

    email_send = SendEmails(emails, message, configuration['ADMIN_EMAIL'], configuration['EMAIL_PORT'])
    email_send.send_email()
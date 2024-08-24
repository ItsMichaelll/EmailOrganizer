"""
This file contains the logic for the email organizer.

Author: Michael Camerato
Date: 8/13/2024
"""

import configparser
import imaplib
import json
import os
import re
import tqdm

TARGET_MAILBOX = '"[Gmail]/All Mail"'
SENDER_LABELS_FILE = "src/data/sender_labels.json"
UNSUBSCRIBED_FILE = "src/data/unsubscribed.json"

EMAIL_REGEX = re.compile(r'<\s*(.*?)\s*>')
BRACKETS_REGEX = re.compile(r'<\s*(.*?)\s*>')

def establish_connection():
    """
    Establishes a connection to the gmail server using the credentials in the config.ini file.

    @return: imaplib.IMAP4_SSL object representing the connection to the gmail server
    """

    config = configparser.ConfigParser()
    config.read("config.ini")

    email_address = config["gmail"]["email"]
    password = config["gmail"]["password"]

    for attempt in range(3):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            break
        except Exception as e:
            if attempt < 2:
                print(f"Connection attempt {attempt+1} failed: {e}. Retrying...")
            else:
                raise Exception(f"Failed to connect to imap.gmail.com after {attempt+1} attempts: {e}")
    mail.login(email_address, password)

    print("Standard Email Organizer > Connection established to Gmail server")
    return mail

def get_sender_rules():
    """
    Fetches the sender rules from the corresponding JSON files.

    @return: dict containing each sender that has been assigned a rule.
    """
    rules = {}
    
    if os.path.exists(SENDER_LABELS_FILE):
        with open(SENDER_LABELS_FILE, "r") as file:
            sender_labels = json.load(file)
            sender_labels = {k: v for k, v in sender_labels.items() if k not in ["Filter by Label", "---"]}
    
    if os.path.exists(UNSUBSCRIBED_FILE):
        with open(UNSUBSCRIBED_FILE, "r") as file:
            unsubscribed = json.load(file)

    for label in sender_labels.keys():
        for address in sender_labels[label]:
            rules[address] = label
    
    for address in unsubscribed:
        rules[address] = "Unsubscribed"
    
    return rules

def fetch_uids(mail):
    """
    Fetches a list of email UIDs from the target mailbox that have not been checked.

    @return: a list of email UIDs cut off at the specified number of emails
    """

    mail.select(TARGET_MAILBOX)

    _, data = mail.search(None, '(NOT X-GM-LABELS "Email Organizer/Standard Organizer/Checked Emails")')

    uids = data[0].split()
    print(
        f"Standard Email Organizer > {len(uids)} emails were fetched from the target mailbox"
    )
    return uids

def get_sender(raw_sender):
    """
    Extracts the sender's email address from an email object.

    @param raw_sender: raw sender string

    @return: email address
    """
    match = BRACKETS_REGEX.search(raw_sender)
    if match:
        return match.group(1)

    else: # bruh
        if(raw_sender.startswith("From: ")):
            raw_sender = f"<{raw_sender[6:]}>"
            return get_sender(raw_sender)



def process_email(mail, uid, rules):
    """
    Processes an email with the given UID.

    @param mail: imaplib.IMAP4_SSL object representing the connection to the gmail server
    @param uid: email UID to process
    @param rules: dictionary containing the sender rules
    """
    
    _, data = mail.uid("FETCH", uid.decode(), "(BODY[HEADER.FIELDS (FROM)])")
    if not data or not data[0]: return
    email_address = get_sender(data[0][1].decode())
    
    mail.uid("STORE", uid, "+X-GM-LABELS", '"Email Organizer/Standard Organizer/Checked Emails"')
    
    if(email_address in rules):
        if rules[email_address] == "Unsubscribed":
            mail.uid("STORE", uid, "+X-GM-LABELS", "\\Trash")
            print(f"Standard Email Organizer > Email from unsubscribed address '{email_address}' was trashed.")
        else:
            mail.uid("STORE", uid, "+X-GM-LABELS", f'"Email Organizer/Standard Organizer/{rules[email_address]}"')
            print(f"Standard Email Organizer > Email from labelled address '{email_address}' was assigned the '{rules[email_address]}' label.")

def organize_emails(mail, uids, rules, cancel_flag=None, progress_callback=None):
    """
    Organizes the emails in the target mailbox based on the rules defined in the Sender List page.

    @param uids: list of email UIDs to organize
    @param cancel_flag: threading.Event object to cancel the organization process (optional)
    @param progress_callback: function to call with the progress of the organization process (optional)
    """
    counter = 0
    total_emails = len(uids)
    with tqdm.tqdm(total=total_emails, desc="Organizing emails...") as pbar:
        for uid in uids:
            if cancel_flag and cancel_flag.is_set():
                print("\nOrganizing cancelled...\n")
                return
            
            process_email(mail, uid, rules)
            counter += 1
            if progress_callback:
                progress_callback(counter / total_emails, pbar.format_dict['n'], pbar.format_dict['total'], pbar.format_dict['rate'], pbar.format_dict['elapsed'])

            pbar.update(1)

    print("Standard Email Organizer > All emails were organized")

def email_organizer(cancel_flag=None, progress_callback=None):
    rules = get_sender_rules()
    mail = establish_connection()
    uids = fetch_uids(mail)
    organize_emails(mail, uids, rules, cancel_flag, progress_callback)

if __name__ == "__main__":
    email_organizer()

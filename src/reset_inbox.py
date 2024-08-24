"""
This file contains the logic for resetting various actions
performed in the Email Organizer application.

Author: Michael Camerato
Date: 8/18/24
"""

import imaplib
import configparser
import json
import os
import re
import tqdm

TARGET_MAILBOX = '"[Gmail]/All Mail"'
SENDER_LABELS_FILE = "src/data/sender_labels.json"
UNSUBSCRIBED_FILE = "src/data/unsubscribed.json"
CATEGORIES_FILE = "src/data/data.json"
SENDER_LIST_FILE = "src/data/senders.json"

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
    mail.login(email_address, password)

    print("Reset Inbox > Connection established to Gmail server")
    return mail

def reset_sender_labels():
    if os.path.exists(SENDER_LABELS_FILE):
        with open(SENDER_LABELS_FILE, "w") as file:
            json.dump({"Filter by Label": [], "---": []}, file, indent=4)

def reset_unsubscribed_senders():
    if os.path.exists(UNSUBSCRIBED_FILE):
        with open(UNSUBSCRIBED_FILE, "w") as file:
            json.dump({}, file, indent=4)

def reset_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "w") as file:
            json.dump({"categories": []}, file, indent=4)

def reset_sender_list():
    if os.path.exists(SENDER_LIST_FILE):
        with open(SENDER_LIST_FILE, "w") as file:
            json.dump([], file, indent=4)

def get_standard_organizer_uids(mail):
    mail.select(TARGET_MAILBOX)
    _, data = mail.uid("SEARCH", None, '(X-GM-LABELS "Email Organizer/Standard Organizer/Checked Emails")')
    uids = data[0].split()
    print(f'Standard Organizer UIDs: {len(uids)}')
    return uids

def get_ai_organizer_uids(mail):
    mail.select(TARGET_MAILBOX)
    _, data = mail.uid("SEARCH", None, '(X-GM-LABELS "Email Organizer/AI Organizer/AI Checked Emails")')
    uids = data[0].split()
    print(f'AI Organizer UIDs: {len(uids)}')
    return uids

def get_labels(mail, uid, label_type=None):
    _, data = mail.uid("FETCH", uid, "(X-GM-LABELS)")
    raw_string = data[0].decode("utf-8")
    match = re.search(r'\(X-GM-LABELS \((.*?)\) UID \d+\)', raw_string)
    labels = re.findall(r'"([^"]+)"', match.group(1))
    if label_type:
        return [label for label in labels if label_type in label]
    return labels

def remove_standard_organizer_labels(progress_callback=None):
    mail = establish_connection()
    uids = get_standard_organizer_uids(mail)

    counter = 0
    total_uids = len(uids)

    with tqdm.tqdm(total=total_uids, desc="Reset Inbox > Removing 'Standard Organizer' labels from UIDs") as pbar:
        for uid in uids:
            labels = get_labels(mail, uid, label_type="Standard Organizer")
            for label in labels:
                mail.uid("STORE", uid, "-X-GM-LABELS", f'"{label}"')
            counter += 1
            if progress_callback:
                progress_callback(counter / total_uids, pbar.format_dict['n'], pbar.format_dict['total'], pbar.format_dict['rate'], pbar.format_dict['elapsed'])
            pbar.update(1)

def remove_ai_organizer_labels(progress_callback=None):
    mail = establish_connection()
    uids = get_ai_organizer_uids(mail)

    counter = 0
    total_uids = len(uids)

    with tqdm.tqdm(total=total_uids, desc="Reset Inbox > Removing 'AI Organizer' labels from UIDs") as pbar:
        for uid in uids:
            labels = get_labels(mail, uid, label_type="AI Organizer")
            for label in labels:
                mail.uid("STORE", uid, "-X-GM-LABELS", f'"{label}"')
            counter += 1
            if progress_callback:
                progress_callback(counter / total_uids, pbar.format_dict['n'], pbar.format_dict['total'], pbar.format_dict['rate'], pbar.format_dict['elapsed'])
            pbar.update(1)

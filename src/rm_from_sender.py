"""
This file contains the logic for removing all emails from a specific sender from the user's inbox.

Author: Michael Camerato
Date: 8/4/24
"""

import imaplib
import configparser
import tqdm

TARGET_MAILBOX = '"[Gmail]/All Mail"'

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

    print("Remove Emails from Sender > Connection established to Gmail server")
    return mail

def fetch_uids_from_sender(mail, sender):
    """
    Fetches a list of all email UIDs from a specific sender
    found in the target mailbox.

    @param sender: the email address of the sender
    
    @return: a list of email UIDs
    """

    mail.select(TARGET_MAILBOX)
    _, data = mail.search(None, f'(FROM "{sender}")')

    uids = data[0].split()
    print(f"Remove Emails from Sender > Found {len(uids)} emails from the email address '{sender}'.")
    return uids

def delete_emails(mail, uids, sender, progress_callback=None):
    """
    This function deletes all emails with the given UIDs
    from the user's target mailbox.

    @param uids: a list of email UIDs
    @param sender: the email address of the sender
    @param progress_callback: a function to call with the progress of the deletion

    """
    with tqdm.tqdm(total=len(uids), desc=f"Deleting {len(uids)} emails from {sender}") as pbar:
        for uid in uids:
            mail.store(uid, '+X-GM-LABELS', '\\Trash')
            pbar.update(1)
            if progress_callback:
                progress_callback(pbar.format_dict['n'] / pbar.format_dict['total'])
    
    mail.expunge()
    mail.close()
    mail.logout()
    print(f"Remove Emails from Sender > Deleted {len(uids)} emails.")

def rm_from_sender(sender, progress_callback=None):
    """
    Main function for this script that remove all emails (from a specific sender)
    from the user's target mailbox.

    @param sender: The email address of the sender to remove emails from.
    @return: None
    """
    mail = establish_connection()
    uids = fetch_uids_from_sender(mail, sender)
    if len(uids) == 0:
        print(f"Remove Emails from Sender > No emails found from {sender}.")
        return
    
    delete_emails(mail, uids, sender, progress_callback)

if __name__ == "__main__":
    sender = input("Enter the email address of the sender to remove emails from: ")
    mail = establish_connection()
    uids = fetch_uids_from_sender(mail, sender)
    cont = input(f"Are you sure you want to delete {len(uids)} emails from {sender}? (y/n): ")
    if cont.lower() == "y": delete_emails(mail, uids, sender)
    else: print("Remove Emails from Sender > Exiting program.")


"""
This script connects to a user's Gmail account, reading the headers of ALL emails in the target folder
to extract the email address and display name for the sender of each email. It then stores this information in a JSON
file 'senders.json'. For each email address entry in the 'senders.json' file, the frequency of emails
received from each sender is included.

Author: Michael Camerato
Date: 8/1/24

"""

import imaplib
import configparser
import email
import json
from multiprocessing import Pool, Manager
import tqdm


TARGET_FOLDER = '"[Gmail]/All Mail"'
SENDERS_FILE = "src/data/senders.json"
BATCH_SIZE = 10

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
    return mail


def fetch_all_uids(mail):
    """
    Fetches a list of emails UIDs for all emails in the target folder.

    @return: list of email UIDs
    """

    mail.select(TARGET_FOLDER)
    _, data = mail.search(None, "ALL")
    uids = data[0].split()
    print(f"Found {len(uids)} emails in the target folder.")
    return uids


def get_sender(email_msg):
    """
    Extracts the sender's name and email address from an email object.

    @param email_msg: email object

    @return: tuple containing the sender's name and email address
    """
    raw_sender = email_msg["From"]
    name, email_address = email.utils.parseaddr(raw_sender)
    return name, email_address


def process_batch(args):
    """
    Helper function to process a batch of emails.
    Designed to be used with multiprocessing.

    @param args: Tuple containing the UID batch, the shared counter, and the should_cancel flag.

    @return: dictionary of senders with their email addresses and frequency counts.
    """
    uid_batch, counter, should_cancel = args
    senders = {}

    mail = establish_connection()
    if not mail: return {}
    mail.select(TARGET_FOLDER)

    for uid in uid_batch:
        if should_cancel.value:
            print("\nBatch processing cancelled.")
            return senders
        try:
            uid = uid.decode()
            _, data = mail.uid("fetch", uid, "(RFC822.HEADER)")
            if not data or not data[0]: continue
            raw_email = data[0][1]
            email_msg = email.message_from_bytes(raw_email)
            name, email_address = get_sender(email_msg)

            if email_address in senders:
                senders[email_address]["frequency"] += 1
            else:
                senders[email_address] = {
                    "name": name,
                    "frequency": 1
                }
        except Exception as e:
            print(f"Error processing email UID {uid}: {e}")
    
    counter.value += 1
    mail.logout()
    return senders


def merge_senders_dicts(dict_list):
    """
    Merges a list of sender dictionaries into a single dictionary.

    @param dict_list: list of sender dictionaries

    @return: merged dictionary of senders
    """
    merged_senders = {}
    for d in dict_list:
        for email_address, info in d.items():
            if email_address in merged_senders:
                merged_senders[email_address]["frequency"] += info["frequency"]
            else:
                merged_senders[email_address] = info
    return merged_senders


def scan_emails_parallel(uids, cancel_flag=None, progress_callback=None):
    """
    Scans the list of email UIDs for senders and their email addresses using parallel processing.

    @param uids: list of email UIDs
    @param cancel_flag: threading.Event object to cancel the scan (optional)
    @param progress_callback: function to call with the progress of the scan (optional)

    Updates the senders.json file with a "sender" entry, which looks like this:

        {
            "Sender's Email Address": {
                "name": "Sender's Name",
                "frequency": # of emails found from sender
            }
        }
    """
    print("Scanning emails with parallel processing...")

    uid_batches = [uids[i:i + BATCH_SIZE] for i in range(0, len(uids), BATCH_SIZE)]
    total_batches = len(uid_batches)

    POOL_SIZE = 10

    with Manager() as manager:
        counter = manager.Value('i', 0)
        should_cancel = manager.Value('b', False)

        with Pool(POOL_SIZE) as pool:
            args = [(batch, counter, should_cancel) for batch in uid_batches]
            
            with tqdm.tqdm(total=total_batches, desc="Processing batches...") as pbar:
                results = []
                for result in pool.imap_unordered(process_batch, args):
                    if cancel_flag and cancel_flag.is_set():
                        should_cancel.value = True
                        pool.terminate()
                        print("\nScan cancelled...\n")
                        return
                    results.append(result)
                    pbar.update(1)
                    if progress_callback:
                        progress_callback(counter.value / total_batches, pbar.format_dict['n'], pbar.format_dict['total'], pbar.format_dict['rate'], pbar.format_dict['elapsed'])

        senders = merge_senders_dicts(results)

        with open(SENDERS_FILE, "w") as file:
            json.dump(senders, file, indent=4)

    print("\nEmails successfully scanned! Scan results saved in 'senders.json' file.\n")


def scan_for_senders(cancel_flag=None, progress_callback=None):
    print("Email scan iniitiated...")
    mail = establish_connection()
    uids = fetch_all_uids(mail)
    mail.logout()
    scan_emails_parallel(uids, cancel_flag, progress_callback)

def main():
    scan_for_senders()

if __name__ == "__main__":
    main()

"""

AI Email Organizer for the application.

This script connects to a user's Gmail account, fetches emails from their inbox,
and then uses Open AI's GPT-4o mini to sort the user's emails into the categories that
they have defined.

Author: Michael Camerato
Date: 7/26/24

"""

import imaplib
import configparser
import email
import re
import json
import os
import html
from openai import OpenAI
from bs4 import BeautifulSoup

MODEL = "gpt-4o-mini"
TARGET_MAILBOX = '"[Gmail]/All Mail"'
CATEGORIES_FILE = "src/data/data.json"
AI_ORGANIZE_OPERATION_RESULT = "ERROR"

# -------------------------------------------------------------------------------------------------------------------
# This variable is VERY IMPORTANT. It is the cut-off point for the email body length.
# Keeping this value low will reduce the total input tokens for the GPT-4o-mini model, and thus reduce the cost.
# Unfortunately, keeping this value low also potentially reduces the accuracy of the model's predictions.
EMAIL_CUTOFF = 2500
# -------------------------------------------------------------------------------------------------------------------

def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "r") as file:
            data = json.load(file)
            return data.get("categories", [])
    return []

def save_categories():
    with open(CATEGORIES_FILE, "w") as file:
        json.dump({"categories": CATEGORIES}, file)

CATEGORIES = load_categories()

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

    print("AI Email Organizer > Connection established to Gmail server")
    return mail

def fetch_uids(mail:imaplib.IMAP4_SSL, num_emails):
    """
    Fetches a list of email UIDs from the target mailbox.

    @param num_emails: the number of emails to fetch
    @return: a list of email UIDs cut off at the specified number of emails
    """

    mail.select(TARGET_MAILBOX)
    _, data = mail.uid("SEARCH", None, '(NOT X-GM-LABELS "Email Organizer/AI Organizer/AI Checked Emails")')

    all_uids = data[0].split()
    if num_emails == "all":
        uids = all_uids
    else:
        uids = all_uids[:num_emails]
    print(
        f"AI Email Organizer > {len(uids)} out of {len(all_uids)} total emails found were fetched from the target mailbox"
    )
    return uids

def log_to_file(uid, json_data):
    LOG_FILE = "src/data/log.json"
    uid = uid.decode("utf-8")
    log_entry = {f"{uid}": json_data}

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            data = json.load(file)
    else: data = {}
    
    data.update(log_entry)

    with open(LOG_FILE, "w") as file:
        json.dump(data, file, indent=4)

def setup_openai_api():
    """
    Sets up the OpenAI API for the application.
    """

    config = configparser.ConfigParser()
    config.read("config.ini")

    api_key = config["openai_api_key"]["api_key"]

    client = OpenAI(api_key=api_key)
    print("AI Email Organizer > OpenAI API service configured")
    return client

def get_email_summary(email_msg):
    """
    Generates a summary of the email content.

    @return summary string
    """

    sender = email_msg["from"]
    subject = email_msg["subject"]
    date = email_msg["date"]
    
    message = f"From: {sender}\nSubject: {subject}\nDate: {date}\n"
    raw_body = ""

    content_types = []

    if email_msg.is_multipart():
        for part in email_msg.walk():
            content_type = part.get_content_type()
            content_types.append(content_type)
        for part in email_msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                raw_body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            elif content_type == "text/html" and "text/plain" not in content_types:
                raw_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(raw_html, 'html.parser')
                for tag in soup.find_all(["div", "p", "span", "td", "li", "h1", "h2", "h3", "a"]):
                    raw_body += tag.get_text(separator=" ", strip=True)
    else:
        raw_body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    raw_body = html.unescape(raw_body)

    clean_body = re.sub(r"<.*?>", "", raw_body)
    clean_body = re.sub(r"\s+", " ", clean_body).strip()
    clean_body = re.sub(r"https?://\S+|www\.\S+", "", clean_body)
    clean_body = clean_body[:EMAIL_CUTOFF]
    message += f"\nBody: {clean_body}\n"

    return message

def organize_emails(mail:imaplib.IMAP4_SSL, uids, client, ai_organizer_flag):
    """
    Uses Generative AI to organize the UIDs of the fetched emails
    into categories specified by the user. As each email's category is
    generated, the email is assigned to the corresponding label.

    @param uids: list of email uids to organize

    @return boolean indicating whether the emails were successfully organized
    """
    global AI_ORGANIZE_OPERATION_RESULT

    successful_moves = 0
    unreadable_emails = 0
    skipped_emails = 0

    mail.select(TARGET_MAILBOX)

    for uid in uids:
        if ai_organizer_flag.is_set():
            print("\nAI Email Organizer > Operation cancelled.")
            AI_ORGANIZE_OPERATION_RESULT = "CANCELLED"
            return False

        try:
            _, data = mail.uid("FETCH", uid.decode(), "(RFC822)")
            if not data or not data[0]:
                raise Exception(f"FETCH ERROR")
            
            raw_email = data[0][1]
            email_msg = email.message_from_bytes(raw_email)
            email_content = get_email_summary(email_msg)
            print('\n------------------------------------------------------------------')
            
            def load_gpt4o_prompt():
                with open("src/data/gpt4o_prompt_template.txt", 'r') as file:
                    content = file.read()
                system_content, prompt_template = content.split("PROMPT_TEMPLATE")
                system_content = system_content.strip(); prompt_template = prompt_template.strip()
                gpt4o_prompt = prompt_template.format(categories=CATEGORIES, email_content=email_content)
                return system_content, gpt4o_prompt

            gpt4o_system_content, gpt4o_prompt = load_gpt4o_prompt()
            
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": gpt4o_system_content},
                    {"role": "user", "content": gpt4o_prompt},
                ]
            )

            response = completion.choices[0].message.content
            print(f"\ngpt4o_prompt: {gpt4o_prompt}\n")
            print(f"\nGPT-4o-mini Response: {response}")

            log_data = {
                "sender": email_msg["from"],
                "subject": email_msg["subject"],
                "date": email_msg["date"],
                "body": email_content,
                "label": response
            }

            if response in CATEGORIES:
                add_label(mail, uid, response, log_data)
                successful_moves += 1
            elif response == "NONE":
                print(f"AI Email Organizer > Email with UID {uid.decode('utf-8')} is either unreadable or doesn't fall into any of the user-defined categories. Assigned label 'Unsure'.")
                add_label(mail, uid, "Unsure", log_data)
                unreadable_emails += 1
            else:
                print(f"AI Email Organizer > Error: Response '{response}' not found in list of categories.")

        except Exception as e:
            if e == "FETCH ERROR":
                fetch_error = f"Error fetching email with UID {uid.decode('utf-8')}. Server Resposne Code {_}, Server Response: {data}"
                print(f"AI Email Organizer > Fetch Error: {fetch_error}")
                log_data = {"fetch_error": fetch_error}
                log_to_file(uid, log_data)
                skipped_emails += 1
                continue
    
    print('\n------------------------------------------------------------------')
    result = f"\nSuccessfully assigned {successful_moves} out of {len(uids)} emails to their corresponding labels."
    if(unreadable_emails > 0):
        result += f"\n{unreadable_emails} emails were unreadable and assigned label \"Unsure\"."
    if(skipped_emails > 0):
        result += f"\n{skipped_emails} emails were skipped due to errors."
    print(result)
    AI_ORGANIZE_OPERATION_RESULT = "SUCCESS"
    return True

def get_labels(mail, uid):
    _, data = mail.uid("FETCH", uid, "(X-GM-LABELS)")
    raw_string = data[0].decode("utf-8")
    match = re.search(r'\(X-GM-LABELS \((.*?)\) UID \d+\)', raw_string)
    labels = re.findall(r'"([^"]+)"', match.group(1))
    for label in labels:
        if label.startswith("\\"):
            label = label[2:]
    return labels

def add_label(mail:imaplib.IMAP4_SSL, uid, label_name, log_data):
    """
    Adds the generated label to an email to categorize it.

    @param uid: the uid of the email to add the label to
    @param label_name: the name of the label to assign the email to

    @return: boolean indicating whether the UID was successfully labeled
    """

    mail.select(TARGET_MAILBOX)

    # Fetch the existing labels for the email
    labels = get_labels(mail, uid)
    print(f"\nAI Email Organizer > Existing labels for email with UID {uid.decode('utf-8')}: {labels}")
    log_data["existing_labels"] = labels

    # Add the label to the email 
    result, data = mail.uid("STORE", uid, "+X-GM-LABELS", f'"Email Organizer/AI Organizer/{label_name}"')
    add_pred_label = {
        "call": f"mail.uid('STORE', {uid}, '+X-GM-LABELS', 'Email Organizer/AI Organizer/{label_name}')",
        "result": result,
        "data": str(data)
    }; log_data["add_pred_label"] = add_pred_label

    # If the label was added successfuly...
    if result == "OK":

        print(f"AI Email Organizer > Email with UID {uid.decode('utf-8')} successfuly assigned label '{label_name}'!")

        # Add the checked label to the email
        result, data = mail.uid("STORE", uid, "+X-GM-LABELS", '"Email Organizer/AI Organizer/AI Checked Emails"')
        add_checked_label = {
            "call": f"mail.uid('STORE', {uid}, '+X-GM-LABELS', '\"Email Organizer/AI Organizer/AI Checked Emails\"')",
            "result": result,
            "data": str(data)
        }; log_data["add_checked_label"] = add_checked_label

        # If the checked label was added successfully...
        if result == "OK":            
            print(f"AI Email Organizer > Email with UID {uid.decode('utf-8')} successfuly marked as checked!")
            return True
        
        # If the checked label was not added successfully...
        else:
            print(f"AI Email Organizer > Error adding label 'Checked' to email with UID {uid.decode('utf-8')}.\
            \tServer result: {result}\tServer response: {data}")
            log_to_file(uid, log_data)
            return False
    
    # If the label was not added successfully...
    else:
        print(f"AI Email Organizer > Error adding label '{label_name}' to email with UID {uid.decode('utf-8')}.\
        \tServer result: {result}\tServer response: {data}")
        log_to_file(uid, log_data)
        return False

def ai_email_organizer(ai_organizer_flag, num_emails):
    """
    Main function for the AI Email Organizer.
    """

    client = setup_openai_api()
    mail = establish_connection()
    uids = fetch_uids(mail, num_emails)
    ai_organizer_flag.set() if not organize_emails(mail, uids, client, ai_organizer_flag) else ai_organizer_flag.clear()
    mail.expunge()
    mail.logout()
    return AI_ORGANIZE_OPERATION_RESULT

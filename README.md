# Email Organizer: An Inbox Organization Tool

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Release Notes](#release-notes)
- [Introduction](#introduction)
- [Features](#features)
  - [Email Organizer](#email-organizer)
  - [AI Organizer](#ai-organizer)
  - [Sender List](#sender-list)
    - [Sender Management Features](#sender-management-features)
  - [Settings](#settings)
- [Installation and Initial Setup](#installation-and-initial-setup)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)

## Release Notes

> ---
> **Release 1.0:**
>
> Initial release of Email Organizer, only available to select users given testing access.
>
> - Many design flaws and poor coding practices are present in this release, but it's a start, and primarily serves as a proof of concept.
>
> - There is enough functionality in this release to be useful and for the testers to provide feedback, which was my primary goal.
>
> - I plan to refactor the entire codebase to follow better coding practices and design patterns, as well as adding more features in addition to improving the existing ones for the next release.
>
> ---
>
> **⚠️ Important Notes ⚠️**
>
> This tool is currently **only compatible with Gmail accounts**
>
> Deleting a sender is currently **irreversible**. Use this feature with caution.
>
> ---

## Introduction

Email Organizer helps users organize and declutter their email inbox, through a user-friendly GUI with all of the features you need just a few clicks away.

Email Organizer started as a personal tool to help me manage my own inbox. I had a Gmail account with over 27,000 emails, and it started to become overwhelming. I looked online for help, and after having trouble finding a tool capable of doing what I was looking for, I decided to just make it myself. I'm a software engineer after all, what could go wrong?

## Features

### Email Organizer

The main feature of Email Organizer, the organizer itself. This feature is only available after you've performed a sender scan in the Sender List tab. Running the organizer will apply the rules that you've established in the Sender List tab to the emails in your inbox, and then add the emails to the label "Checked".

### AI Organizer

Take advantage of AI to organize your emails into categories that you define.

Create a list of categories that you think are relevant to your inbox, and the AI will do the rest! Just select whether you'd like to organize all emails at once or a select number of emails, start the organizer, and watch the magic happen!

### Sender List

This is where you can manage your list of email senders and establish rules for how you'd like your inbox to be organized during the organizer process.

If you haven't performed a sender scan, you'll need to do so in order to access the sender management features.

#### Sender Management Features

Manage your list of email senders from the sender scan. You can search for specific senders and sort the list, as well as applying filters to see senders you've labeled.

Want to delete a sender from your list and trash all of their emails? Simply click the 'Delete Sender' button.

Add rules that will be applied whenever you run the organize process in the Email Organize tab:

- **Unsubscribe** from senders to have all of their emails sent to the trash folder in the email organizer process.
- **Add labels** to senders to have them labeled in the email organizer process.

### Settings

Reset certain actions performed in the Email Organizer. You can reset:

- User-defined categories in the AI Organizer
- All labels assigned to senders in the Sender List
- All senders marked as unsubscribed in the Sender List
- The entire Sender List (you'll need to do a new scan!)

Additionally, there are options for a "Fresh Start" for both the Email Organizer and AI Organizer, which remove all labels assigned during their respective processes from the emails in your inbox.

## Installation and Initial Setup

**NOTE:** It is **crucial** that you follow **every step** listed here! Failure to do so *may* result in the application not working as expected, which will inevitably lead to unexpected glitches and bugs.

1. Clone the repository:

    ```shell
    git clone https://github.com/ItsMichaelll/EmailOrganizer.git
    ```

2. Navigate to the repository's directory:

    ```shell
    cd EmailOrganizer
    ```

3. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```

4. Configure your credentials in the `config.ini` file found in the root directory of the repository:

    ```ini
    [gmail]
    email = your_email@gmail.com
    password = your_app_password

    [openai_api_key]
    api_key = openai_api_key
    ```

    For the Gmail credentials, it's not wise to use your Google account's password. Instead, please generate an 'App Password' via the [Google App Passwords](https://myaccount.google.com/apppasswords) website.

    For the OpenAI API credentials, you have a couple of options. You can either...
    - Generate an OpenAI API key [here](https://platform.openai.com/account/api-keys) acknowledging that you'll be charged for using the API
    - Opt out of using the AI Organizer features by leaving the `api_key` field blank.

    ***Note:*** *If you're a tester, you'll receive my personal API key. Copy and paste this into the `api_key` field. Happy testing!*

5. Ensure that you have IMAP access enabled in your Gmail account settings:

    Visit the [Forwarding and POP/IMAP section](https://mail.google.com/mail/u/0/#settings/fwdandpop) of your Gmail account settings.

    Under the "IMAP access" section, make sure that "Enable IMAP" is selected.

    Your settings should look like this:

    ![Gmail IMAP Settings](https://prnt.sc/LE_OaRk8u0xc "Gmail IMAP Settings")

6. Finally, make sure that your Gmail account has the following label heirarchy setup:

    ![Gmail Label Heirarchy](https://prnt.sc/37-Bn5ekwF3e "Gmail Label Heirarchy")

## Usage

1. Run the application:

    ```shell
    python -m src.GUI.App
    ```

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any questions, don't hesitate to reach out to me personally at [camerato91703@gmail.com](mailto:camerato91703@gmail.com).

"""
This file defines the 'SenderEntry' class, which contains information about a sender
as well as a CTkFrame object for the GUI to display the sender's information.

Author: Michael Camerato
Date: 8/3/24
"""

import json
import os
import threading
import customtkinter as ctk
from .GUI.AppStyles import *

class SenderEntry:
    def __init__(self, email_address, name, frequency, add_label_callback,
      unsubscribe_callback, resubscribe_callback, delete_callback):
        self.address = email_address
        self.name = name
        self.frequency = frequency

        self.add_label_callback = add_label_callback
        self.unsubscribe_callback = unsubscribe_callback
        self.resubscribe_callback = resubscribe_callback
        self.delete_callback = delete_callback

        self.sender_txt_frame = None

        self.email_address_label = None
        self.email_name_label = None
        self.email_frequency_label = None
        
        self.adding_label = False
        self.deleting_sender = False

        self.add_label_button = None
        self.add_label_entry = None
        self.add_label_confirm_button = None

        self.rm_sender_thread = None
        self.rm_sender_cancel_flag = threading.Event()

    def __str__(self):
        if self.name == "":
            return f"Email Address: {self.address}," \
                + f" Emails Sent: {self.frequency}"
        
        return f"Email Address: {self.address}," \
            + f" Name: {self.name}," \
            + f" Emails Sent: {self.frequency}"

    def get_email_address(self):
        return self.address

    def get_name(self):
        return self.name

    def get_frequency(self):
        return self.frequency

    def __lt__(self, other):
        if not isinstance(other, SenderEntry):
            return NotImplemented
        return self.frequency < other.frequency
    
    def __eq__(self, other):
        if not isinstance(other, SenderEntry):
            return NotImplemented
        return self.frequency == other.frequency

    def create_entry(self, master, first_email=False):
        self.sender_frame = ctk.CTkFrame(
            master=master,
            fg_color=SenderEntryFG,
            corner_radius=0
        )
        
        y_padding = (5, 5) if first_email else (0, 5)
        self.sender_frame.pack(padx=5, pady=y_padding, fill="x", expand=True)

        self.sender_txt_frame = ctk.CTkFrame(
            self.sender_frame,
            fg_color="transparent"
        )

        # Sender Email Address
        self.email_address_label = ctk.CTkLabel(
            self.sender_txt_frame,
            text=f"{self.address}",
            font=SenderEntryAddressFont
        )
        self.email_address_label.pack(anchor="w", padx=12, pady=(12, 0))


        # Sender Name
        self.email_name_label = ctk.CTkLabel(
            self.sender_txt_frame,
            text=f"{self.name}" if self.name else "",
            font=SenderEntryNameFont
        )
        self.email_name_label.pack(anchor="w", padx=12, pady=(6, 0))

        # Amount of Emails Received from Sender
        self.email_frequency_label = ctk.CTkLabel(
            self.sender_txt_frame,
            text=f"Emails Received: {self.frequency}",
            font=SenderEntryFreqFont
        )
        self.email_frequency_label.pack(anchor="w", padx=12, pady=(6, 12))

        # Delete Sender Button
        self.delete_sender_button = ctk.CTkButton(
            self.sender_frame,
            height=40,
            text="Delete Sender",
            font=SenderEntryBtnFont,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.delete
        )
        self.delete_sender_button.pack(padx=(6,12), pady=6, side="right")

        self.delete_sender_label = ctk.CTkLabel(
            self.sender_txt_frame,
            text=f"Trash all emails from {self.address}?",
            font=("Switzer Medium", 16),
        )
        self.delete_sender_confirm_button = ctk.CTkButton(
            self.sender_txt_frame,
            text="Delete Sender",
            font=SenderEntryBtnFont,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.delete_confirm
        )
        self.delete_sender_pbar = ctk.CTkProgressBar(
            self.sender_txt_frame,
            width=500,
            height=16,
            progress_color=LIGHT_RED
        )
        self.delete_sender_pbar.set(0)

        # Unsubscribe/Resubscribe Button
        self.subscription_button = ctk.CTkButton(
            self.sender_frame,
            height=40,
            text="Unsubscribe",
            font=SenderEntryBtnFont,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.unsubscribe
        )

        self.init_sub_button()
        self.subscription_button.pack(padx=6, pady=6, side="right")

        # Add Label Button
        self.add_label_button = ctk.CTkButton(
            self.sender_frame,
            height=40,
            text="Add Label",
            font=SenderEntryBtnFont,
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            command=self.add_label
        )
        self.add_label_button.pack(padx=6, pady=6, side="right")

        self.add_label_entry = ctk.CTkEntry(
            self.sender_txt_frame,
            width=200,
            placeholder_text="Enter label name",
            font=("Switzer Medium", 18),
            fg_color=ENTRY_FG,
            border_width=0,
            corner_radius=0
        )
        
        self.add_label_label = ctk.CTkLabel(
            self.sender_txt_frame,
            text=f"Add a label to all emails from {self.address}:",
            font=("Switzer Medium", 16),
        )
        self.add_label_confirm_button = ctk.CTkButton(
            self.sender_txt_frame,
            width=200,
            text="Confirm",
            font=SenderEntryBtnFont,
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            corner_radius=2,
            command=self.add_label_confirm
        )
        
        self.sender_txt_frame.pack(padx=0, pady=0, fill="x", side="left")
    
    def add_label(self):
        self.adding_label = not self.adding_label

        # Adding Label Toggled Off
        if(not self.adding_label):
            self.sender_frame.update()

            self.subscription_button.configure(state="normal")
            self.delete_sender_button.configure(state="normal")

            self.add_label_button.configure(
                text="Add Label",
                fg_color=DARK_BLUE,
                hover_color=DARK_BLUE_HOVER
            )

            self.add_label_label.pack_forget()
            self.add_label_entry.pack_forget()
            self.add_label_confirm_button.pack_forget()

            self.email_address_label.pack(anchor="w", padx=12, pady=(12, 0))
            self.email_name_label.pack(anchor="w", padx=12, pady=(6, 0))
            self.email_frequency_label.pack(anchor="w", padx=12, pady=(6, 12))

            self.sender_frame.update()
        
        # Adding Label Toggled On
        else:
            self.sender_frame.update()

            self.subscription_button.configure(state="disabled")
            self.delete_sender_button.configure(state="disabled")

            self.add_label_button.configure(
                text="Cancel",
                fg_color=LIGHT_BLUE,
                hover_color=LIGHT_BLUE_HOVER
            )

            self.email_address_label.pack_forget()
            self.email_name_label.pack_forget()
            self.email_frequency_label.pack_forget()

            self.add_label_label.pack(anchor="w", padx=12, pady=(12, 0))
            self.add_label_entry.pack(anchor="w", padx=12, pady=(6, 0))
            self.add_label_confirm_button.pack(anchor="w", padx=12, pady=(6, 12))

            self.sender_frame.update()

    def add_label_confirm(self):
        label = self.add_label_entry.get().strip()

        if label:
            self.add_label_entry.delete(0, 'end')
            self.add_label_callback(self.address, label)
            self.add_label()

    def unsubscribe(self):
        self.unsubscribe_callback(self.address)
        self.unsubscribed = True
        self.update_sub_button()

    def resubscribe(self):
        self.resubscribe_callback(self.address)
        self.unsubscribed = False
        self.update_sub_button()

    def delete(self):
        self.deleting_sender = not self.deleting_sender

        # Delete Sender Toggled Off
        if(not self.deleting_sender):
            self.sender_frame.update()

            self.add_label_button.configure(state="normal")
            self.subscription_button.configure(state="normal")

            self.delete_sender_button.configure(
                text="Delete Sender",
                fg_color=DARK_RED,
                hover_color=DARK_RED_HOVER
            )

            self.delete_sender_label.pack_forget()
            self.delete_sender_confirm_button.pack_forget()
            self.delete_sender_pbar.pack_forget()
            
            self.email_address_label.pack(anchor="w", padx=12, pady=(12, 0))
            self.email_name_label.pack(anchor="w", padx=12, pady=(6, 0))
            self.email_frequency_label.pack(anchor="w", padx=12, pady=(6, 12))

            self.sender_frame.update()
        
        # Delete Sender Toggled On
        else:
            self.sender_frame.update()

            self.add_label_button.configure(state="disabled")
            self.subscription_button.configure(state="disabled")


            self.delete_sender_button.configure(
                text="Cancel",
                fg_color=LIGHT_RED,
                hover_color=LIGHT_RED_HOVER
            )

            self.email_address_label.pack_forget()
            self.email_name_label.pack_forget()
            self.email_frequency_label.pack_forget()

            self.delete_sender_label.pack(anchor="w", padx=12, pady=(12, 0))
            self.delete_sender_confirm_button.pack(anchor="w", padx=12, pady=(6, 12))
            self.delete_sender_pbar.pack(anchor="w", padx=12, pady=(6, 12), fill="x", expand=True)

            self.sender_frame.update()

    def delete_confirm(self):
        if not hasattr(self, 'delete_in_progress') or not self.delete_in_progress:
            self.delete_in_progress = True
            self.sender_frame.update()

            self.add_label_button.destroy()
            self.subscription_button.destroy()
            self.delete_sender_button.destroy()

            self.delete_sender_label.configure(text=f"Trashing all emails from {self.address}...")
            self.delete_sender_confirm_button.configure(state="disabled", text="Deleting...")

            self.delete_callback(self.delete_sender_pbar, self.address)
        else:
            print(f"SenderEntry 'DELETE' > A delete operation is already in progress for sender {self.address}")

    def init_sub_button(self):
        if os.path.exists("src/data/unsubscribed.json"):
            with open("src/data/unsubscribed.json", "r") as file:
                data = json.load(file)
            if self.address in data: self.unsubscribed = True
            else: self.unsubscribed = False
            self.update_sub_button()

    def update_sub_button(self):
        if self.unsubscribed:
            self.subscription_button.configure(
                text="Resubscribe",
                command=self.resubscribe,
                fg_color=DARK_BLUE,
                hover_color=DARK_BLUE_HOVER
            )
        else:
            self.subscription_button.configure(
                text="Unsubscribe",
                command=self.unsubscribe,
                fg_color=DARK_RED,
                hover_color=DARK_RED_HOVER
            )

import json
import os
import threading
import customtkinter as ctk

from src.GUI.AppStyles import *
from src.email_organizer import email_organizer

class EmailOrganizer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            corner_radius=0,
            fg_color='transparent'
        )
        self.has_scanned_senders = self.check_has_scanned_senders()
        self.has_rules = self.check_has_rules()
        self.init_descs()

        self.scan_thread = None
        self.scan_cancel_flag = threading.Event()

        if(not self.has_scanned_senders):
            self.missing_step("scan")
        elif(not self.has_rules):
            self.missing_step("rules")
        else:
            self.setup_scan_button()

        self.pack(padx=12, pady=12, fill="both", expand=True)
    
    def check_has_scanned_senders(self):
        file_exists = os.path.exists("src/data/senders.json")
        if file_exists:
            with open("src/data/senders.json", "r") as file:
                if len(json.load(file)) == 0: return False
                else: return True
        elif not file_exists:
            with open("src/data/senders.json", "w") as file:
                json.dump([], file, indent=4)
            return False

    def check_has_rules(self):
        """
        Checks if any senders have been assigned labels,
        or if any senders have been unsubscribed from.

        @return: bool indicating if any rules have been setup.
        """
        if os.path.exists("src/data/sender_labels.json"):
            with open("src/data/sender_labels.json", "r") as file:
                data = json.load(file)
                for sender in data:
                    if(sender not in ["Filter by Label", "---"]):
                        if(len(data[sender]) > 0):
                            return True
        
        if os.path.exists("src/data/unsubscribed.json"):
            with open("src/data/unsubscribed.json", "r") as file:
                data = json.load(file)
                if(len(data) > 0): return True
        return False

    def init_descs(self):
        self.desc1 = ctk.CTkLabel(master=self,
            text="Here, you can organize your inbox and keep it up-to-date." \
                +"\nYour inbox will be sorted into categories based on the labels that you setup in the Sender List page.",
            font=("Switzer Semibold", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        )
        self.desc2 = ctk.CTkLabel(master=self,
            text="In order for your inbox to be sorted, you must first scan your inbox for a list of senders." \
                + "\nAfterwards, you will have the opportunity to:" \
                + "\n\n• Add labels to specific senders (sorts their emials during this scan)" \
                + "\n\n• Unsubscribe from a specific sender (trashes their emails during this scan)",
            font=("Switzer", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        )
        self.desc1.pack(padx=12, pady=12, fill="both"); self.desc2.pack(padx=12, pady=12, fill="both")

    def missing_step(self, missing_step):
        self.desc3 = ctk.CTkLabel(
            master=self,
            text="",
            font=("Switzer", 26, "bold"),
            wraplength=1000,
            justify="left",
            anchor="w",
        )
        if(missing_step == "scan"):
            self.desc3.configure(text="It appears you haven't performed a sender scan yet!" \
                                 + "\nPlease go to the Sender List page and perform a scan first.")
        if(missing_step == "rules"):
            self.desc3.configure(text="You need to have custom rules setup first!" \
                                 + "\nPlease go to the Sender List page and setup some rules for specific senders"\
                                + "\n(i.e. add labels, unsubscribe)")
        self.desc3.pack(padx=12, pady=12, fill="both")
    
    def setup_scan_button(self):
        self.scan_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.scan_frame.pack(padx=12, pady=12, fill="x")
        
        self.scan_button = ctk.CTkButton(
            master=self.scan_frame,
            height=50,
            width=300,
            text="Organize Inbox",
            font=("Switzer Black", 28),
            fg_color=DARK_BLUE_HOVER,
            hover_color=DARK_BLUE,
            corner_radius=12,
            command=self.scan,
        )
        self.scan_button.pack(padx=12, pady=12, side="left")

    def scan(self):
        self.scan_cancel_flag.clear()
        self.master.master.master.disable_sidebar_links()
        self.scan_button.pack_forget()

        self.cancel_scan_button = ctk.CTkButton(
            master=self.scan_frame,
            height=50,
            width=300,
            text="Cancel",
            font=("Switzer Black", 28),
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.cancel_scan,
        ); self.cancel_scan_button.pack(padx=12, pady=12, side="left")

        self.scan_pframe = ctk.CTkFrame(self, fg_color="transparent")
        self.scan_pframe.pack(padx=12, pady=12, fill="x")

        self.scan_pbar_label_1 = ctk.CTkLabel(
            master=self.scan_pframe,
            text="0%",
            font=("Switzer", 24, "bold"),
        ); self.scan_pbar_label_1.pack(padx=(12, 6), pady=12, side="top")

        self.scan_pbar = ctk.CTkProgressBar(
            master=self.scan_pframe,
            width=500,
            height=20,
            progress_color=LIGHT_BLUE
        )
        self.scan_pbar.set(0)
        self.scan_pbar.pack(padx=(6, 12), pady=12, side="top", fill="x")

        self.scan_thread = threading.Thread(target=self.run_scan)
        self.scan_thread.start()
        self.after(100, self.check_scan_status)

    def run_scan(self):
        email_organizer(self.scan_cancel_flag, self.update_scan_progress)

    def update_scan_progress(self, progress, n, total, rate, elapsed):
        if(n==0): return
        
        remaining_seconds = ((total - n) / rate)

        elapsed_hours = int(elapsed // 3600)
        elapsed_minutes = int((elapsed % 3600) // 60)
        elapsed_seconds = int(elapsed % 60)
        time_elapsed = f'{elapsed_hours}:{elapsed_minutes:02}:{elapsed_seconds:02}'

        remaining_hours = int(remaining_seconds // 3600)
        remaining_minutes = int((remaining_seconds % 3600) // 60)
        remaining_seconds = int(remaining_seconds % 60)
        time_remaining = f'{remaining_hours}:{remaining_minutes:02}:{remaining_seconds:02}'

        self.scan_pbar.set(progress)
        self.scan_pbar_label_1.configure(text=f"{progress:.1%} | {time_elapsed} elapsed / {time_remaining} remaining | {rate:.2f} emails/s")

    def check_scan_status(self):
        if self.scan_thread is not None and self.scan_thread.is_alive():
            self.after(100, self.check_scan_status)
        else:
            self.master.master.master.enable_sidebar_links()
            self.cancel_scan_button.destroy()
            self.scan_pbar.destroy()
            self.scan_pbar_label_1.destroy()
            self.scan_pframe.destroy()
            self.scan_button.pack(padx=12, pady=12, side="left")
    
    def cancel_scan(self):
        self.scan_cancel_flag.set()
        self.cancel_scan_button.configure(state="disabled", text="Cancelling...")
        self.after(100, self.check_scan_status)


from email.header import decode_header
import os, json
import quopri
import re
import customtkinter as ctk
import threading
from PIL import Image

from ..sender_scan import BATCH_SIZE, scan_for_senders
from ..SenderEntry import SenderEntry
from ..rm_from_sender import rm_from_sender

from .AppStyles import *

class SenderList(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            corner_radius=0,
            fg_color='transparent'
        )

        self.has_scanned = self.check_has_scanned()
        self.sortedby = [None, None]
        self.searched = False
        self.is_filtered = False

        self.init_descs()

        self.scan_button = None
        self.scan_thread = None
        self.scan_cancel_flag = threading.Event()
        self.scan_pbar = None
        self.scan_pbar_label_1 = None

        self.delete_sender_thread = None
        self.delete_sender_pbar = None
        self.delete_sender_address = None

        self.exit_search_button = None

        self.pack(padx=12, pady=12, fill="both", expand=True)
        
        if not self.has_scanned: self.hasnt_scanned_display()
        else: self.has_scanned_display()

    
    def check_has_scanned(self):
        if os.path.exists("src/data/senders.json"):
            with open("src/data/senders.json", "r") as file:
                try:
                    data = json.load(file)
                    if data: return True
                    return False
                except: return False
        return False

    def init_descs(self):
        self.desc_1 = ctk.CTkLabel(
            master=self,
            text="",
            font=("Switzer Semibold", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.desc_1.pack(padx=12, pady=12, fill="both")

        self.desc_2 = ctk.CTkLabel(
            master=self,
            text="",
            font=("Switzer", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.desc_2.pack(padx=12, pady=12, fill="both")

    def hasnt_scanned_display(self):
        self.desc_1.configure(
            text="It appears you haven't scanned your inbox for a list of senders yet. Once you do, you can...",
        )

        self.desc_2.configure(
            text="• Add a label to a sender and have all of their emails assigned to that label\n\n" \
                + "• Delete a sender and have all of their emails trashed\n\n" \
                + "• Unsubscribe from a sender to stop receiving emails from them",
        )

        self.desc_3 = ctk.CTkLabel(
            master=self,
            text="** Please note that this process may take a while, depending on the amount of emails in your inbox." \
                + "\n\n** You will be unable to use the application during the scan, though you may cancel the scan at any time.",
            font=("Switzer", 20, "italic"),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.desc_3.pack(padx=12, pady=12, fill="both")

        self.scan_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.scan_frame.pack(padx=12, pady=12, fill="x")
        
        self.scan_button = ctk.CTkButton(
            master=self.scan_frame,
            height=50,
            width=300,
            text="Start Scan",
            font=("Switzer Black", 28),
            fg_color=DARK_BLUE_HOVER,
            hover_color=DARK_BLUE,
            corner_radius=12,
            command=self.scan,
        ); self.scan_button.pack(padx=12, pady=12, side="left")

    def has_scanned_display(self):
        self.desc_1.configure(
            text="Below, you can view a list of senders you've received emails from. You can...",
        )

        self.desc_2.configure(
            text="• Add a label to a sender to have all of their emails (new AND old) categorized during the email organizer operation\n\n" \
                + "• Unsubscribe from a sender to have all of their emails (new AND old) trashed during the email organizer operation\n\n" \
                + "• Delete a sender to have all of their emails trashed immediately (this may take some time)\n\n" \
        )

        self.senders = []
        self.page_size = 20
        self.total_pages = (len(self.senders) + self.page_size - 1) // self.page_size
        self.current_page = 1

        self.filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filters_frame.pack(padx=12, pady=12, fill="x")
        self.display_filters()

        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(padx=12, pady=12, fill="x")
        self.display_search()
        self.update()

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=100,
            fg_color=Level2PageFrameFG,
            corner_radius=5,
            border_width=0
        ); self.scrollable_frame.pack(
            padx=12,
            pady=12,
            side="top",
            fill="both",
            expand=True
        )

        self.pagination_frame = ctk.CTkFrame(
            master=self,
            fg_color=SenderPaginationFG,
            corner_radius=5
        ); self.pagination_frame.pack(padx=12, pady=0, fill="both")

        self.pagination_frame.grid_columnconfigure(0, weight=1)
        self.pagination_frame.grid_columnconfigure((1,2,3), weight=0)
        self.pagination_frame.grid_columnconfigure(4, weight=1)

        self.prev_button = ctk.CTkButton(
            self.pagination_frame,
            width=100,
            text="Previous",
            font=("Switzer", 20, "bold"),
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            command=self.prev_page
        ); self.prev_button.grid(row=0, column=1, pady=6)

        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text=f"Page {self.current_page} of {self.total_pages}",
            font=("Switzer", 32, "bold"),
        ); self.page_label.grid(row=0, column=2, padx=15, pady=6)

        self.next_button = ctk.CTkButton(
            self.pagination_frame,
            width=100,
            text="Next",
            font=("Switzer", 20, "bold"),
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            command=self.next_page,
        ); self.next_button.grid(row=0, column=3, pady=6)

        self.pagination_frame.bind("<MouseWheel>", self.pagination_scroll)
        self.prev_button.bind("<MouseWheel>", self.pagination_scroll)
        self.page_label.bind("<MouseWheel>", self.pagination_scroll)
        self.next_button.bind("<MouseWheel>", self.pagination_scroll)

        self.load_senders_thread = threading.Thread(target=self.load_senders_threaded)
        self.load_senders_thread.start()

    def load_senders_threaded(self):
        self.senders = self.load_senders()
        self.total_pages = (len(self.senders) + self.page_size - 1) // self.page_size
        self.current_page = 1
        self.after(0, self.display_senders)

    def load_senders(self):
        with open("src/data/senders.json", "r") as file:
            senders_data = json.load(file)
        
        eq_reg = re.compile(r'^=\?')
        for sender in senders_data:
            raw_name = senders_data[sender]['name']
            if eq_reg.match(raw_name):
                decoded_parts = decode_header(raw_name)
                decoded_name = ''
                for part, encoding in decoded_parts:
                    if isinstance(part, bytes):
                        if encoding:
                            decoded_name += part.decode(encoding)
                        else:
                            decoded_name += quopri.decodestring(part).decode('utf-8', errors='ignore')
                    else:
                        decoded_name += part
                
                senders_data[sender]['name'] = decoded_name.strip()

        return sorted(senders_data.items(), key=lambda x: x[1]['name'])

    def display_senders(self):
        for widget in self.scrollable_frame.winfo_children():
            try: widget.destroy()
            except Exception as e: print(f"Error destroying widget: {e}")

        if not self.senders:
            return

        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        page_senders = self.senders[start:end]

        for i, (email, data) in enumerate(page_senders):
            try:
                sender_entry = SenderEntry(
                    email, data['name'], data['frequency'],
                    self.add_label, self.unsubscribe,
                    self.resubscribe, self.delete_sender
                )
                if i == 0: sender_entry.create_entry(self.scrollable_frame, first_email=True)
                else: sender_entry.create_entry(self.scrollable_frame)
            except Exception as e:
                print(f"Error creating sender entry for {email}: {e}")

        self.update_pagination_controls()

    def display_filters(self):
        # 'Sort by:' Label
        self.sortby_label = ctk.CTkLabel(
            self.filters_frame,
            text="Sort by:",
            font=("Switzer Black", 24),
        ); self.sortby_label.pack(side="left", padx=(0, 5))

        # Sort by Email Address button
        self.sort_email_btn = ctk.CTkButton(
            self.filters_frame,
            width=200,
            height=40,
            text=f"Email",
            font=("Switzer Black", 18),
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            corner_radius=SortBtnCornerRadius,
            command=lambda: self.handle_sort('email')
        ); self.sort_email_btn.pack(side="left", padx=5)

        # Sort by Name button
        self.sort_name_btn = ctk.CTkButton(
            self.filters_frame,
            width=200,
            height=40,
            text=f"Name",
            font=("Switzer Black", 18),
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            corner_radius=SortBtnCornerRadius,
            command=lambda: self.handle_sort('name')
        ); self.sort_name_btn.pack(side="left", padx=5)
    
        # Sort by Frequency button
        self.sort_frequency_btn = ctk.CTkButton(
            self.filters_frame,
            width=200,
            height=40,
            text=f"Emails Received",
            font=("Switzer Black", 18),
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            corner_radius=SortBtnCornerRadius,
            command=lambda: self.handle_sort('emails received')
        ); self.sort_frequency_btn.pack(side="left", padx=5)

        # Filter by Label Dropdown
        self.filter_label_dd = ctk.CTkOptionMenu(
            self.filters_frame,
            width=200,
            height=40,
            font=("Switzer Black", 18),
            dropdown_font=("Switzer", 18, "bold"),
            text_color='#FFF',
            dropdown_text_color='#FFF',
            fg_color=DARKER_BLUE,
            dropdown_fg_color=DARKER_BLUE,
            button_color=DARK_BLUE,
            button_hover_color=DARK_BLUE_HOVER,
            dropdown_hover_color=DARKER_BLUE_HOVER,
            values=["Filter by Label"],
            anchor="center",
            dynamic_resizing=False,
            corner_radius=SortBtnCornerRadius,
            command=self.handle_filter
        ); self.update_filter_dd()
        self.filter_label_dd.pack(side="left", padx=5)

    def display_search(self):
        self.search_label = ctk.CTkLabel(
            self.search_frame,
            text="Search:",
            font=("Switzer", 24, "bold"),
        ); self.search_label.pack(side="left", padx=(0, 5))

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            width=530,
            height=45,
            placeholder_text="Search...",
            font=("Switzer Semibold", 18),
            fg_color=ENTRY_FG,
            corner_radius=2,
            border_width=0
        ); self.search_entry.pack(side="left", padx=(8,0))
        self.search_entry.bind("<Return>", self.search_senders)

        self.search_button = ctk.CTkButton(
            self.search_frame,
            width=90,
            height=45,
            text="🔍",
            font=("Switzer", 26, "bold"),
            anchor="center",
            corner_radius=0,
            fg_color=DARK_BLUE,
            hover_color=DARK_BLUE_HOVER,
            command=self.search_senders
        ); self.search_button.pack(side="left", padx=2)

        self.exit_search_button = ctk.CTkButton(
            self.search_frame,
            width=90,
            height=45,
            text="×",
            font=("Switzer Black", 22),
            anchor="center",
            corner_radius=0,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=lambda: self.toggle_searched(False)
        )

    def handle_sort(self, key):
        if self.sortedby[0] == key:
            # Reverse the sort order if the same key is clicked again
            self.sortedby[1] = '↓' if self.sortedby[1] == '↑' else '↑'
        else:
            # Set new key and default to descending order
            self.sortedby = [key, '↑']

        reverse = self.sortedby[1] == '↓'

        if key == 'email':
            self.senders.sort(key=lambda x: x[0].lower(), reverse=reverse)
        elif key == 'name':
            self.senders.sort(key=lambda x: (x[1]['name'] == '', x[1]['name'].lower()), reverse=reverse)
        elif key == 'emails received':
            self.senders.sort(key=lambda x: x[1]['frequency'], reverse=not reverse) # for some reason frequency is reversed

        self.current_page = 1
        self.display_senders()
        self.update_sort_buttons()

    def handle_filter(self, label):
        if label in ["Filter by Label", "---"]:
            if(self.is_filtered):
                self.senders = self.load_senders()
                self.total_pages = (len(self.senders) + self.page_size - 1) // self.page_size
                self.current_page = 1
                self.display_senders()
                self.update_pagination_controls()
            
            self.filter_label_dd.set("Filter by Label")
            self.is_filtered = False
            return
        
        self.is_filtered = True
        print(f"Filtering by label: {label}")

        with open("src/data/sender_labels.json", "r") as file:
            label_data = json.load(file)
        
        filtered_emails = label_data.get(label, [])
        self.senders = [
            (email, data) for email, data in self.load_senders()
            if email in filtered_emails
        ]

        self.search_entry.delete(0, ctk.END)
        self.total_pages = (len(self.senders) + self.page_size - 1) // self.page_size
        self.current_page = 1
        self.display_senders()
        self.update_pagination_controls()

    def update_sort_buttons(self):
        asc_img = ctk.CTkImage(
            light_image=Image.open("src/assets/sort ascending indicator (black).png"),
            dark_image=Image.open("src/assets/sort ascending indicator (white).png"),
            size=(25, 25))
        desc_img = ctk.CTkImage(
            light_image=Image.open("src/assets/sort descending indicator (black).png"),
            dark_image=Image.open("src/assets/sort descending indicator (white).png"),
            size=(25, 25))

        for btn, sort_key in [(self.sort_email_btn, 'email'), 
                              (self.sort_name_btn, 'name'), 
                              (self.sort_frequency_btn, 'emails received')]:
            if self.sortedby[0] == sort_key:
                btn.update()
                btn.configure(
                    image=asc_img if self.sortedby[1] == '↑' else desc_img,
                    fg_color=LIGHT_BLUE,
                    hover_color=LIGHT_BLUE_HOVER,
                    compound="right"
                ); btn.update()
            else:
                btn.update()
                btn.configure(
                    image=None,
                    fg_color=DARK_BLUE,
                    hover_color=DARK_BLUE_HOVER,
                ); btn.update()

    def search_senders(self, event=None):
        search_query = self.search_entry.get()
        if search_query == "":
            if not self.searched: return
            else:
                print(f'resetting search...')
                self.toggle_searched(False)
                self.senders = self.load_senders()
        else:
            print(f'searching for "{search_query}"...')
            self.toggle_searched(True)
            self.senders = [
                (email, data) for email, data in self.load_senders()
                if search_query in email.lower()
                or search_query in data['name'].lower()
            ]
        
        self.total_pages = (len(self.senders) + self.page_size - 1) // self.page_size
        self.current_page = 1
        self.display_senders()
        self.update_pagination_controls()

    def toggle_searched(self, searched: bool):
        self.searched = searched
        if self.searched:
            self.exit_search_button.pack(side="left", fill="x", padx=1)
        else:
            print(f'resetting search...')
            self.search_entry.delete(0, ctk.END)
            self.exit_search_button.pack_forget()
            self.senders = self.load_senders()
            self.total_pages = (len(self.senders) + self.page_size - 1) // self.page_size
            self.current_page = 1
            self.display_senders()
            self.update_pagination_controls()

    def update_pagination_controls(self):
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages}")
        self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_button.configure(state="normal" if self.current_page < self.total_pages else "disabled")

    def pagination_scroll(self, event):
        if event.delta > 0: self.prev_page()
        else: self.next_page()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_senders()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_senders()

    def scan(self):
        self.scan_cancel_flag.clear()
        self.master.master.master.disable_sidebar_links()
        self.scan_button.pack_forget()
        
        self.cancel_scan_button = ctk.CTkButton(
            master=self.scan_frame,
            height=50,
            width=300,
            text="Cancel Scan",
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
        scan_for_senders(self.scan_cancel_flag, self.update_scan_progress)
        if not self.scan_cancel_flag.is_set():
            self.has_scanned = True

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

        self.after(0, self.scan_pbar.set(progress))
        self.scan_pbar_label_1.configure(text=f"{progress:.1%} | {time_elapsed} elapsed / {time_remaining} remaining | {rate*BATCH_SIZE:.2f} emails/s")

    def check_scan_status(self):
        if self.scan_thread is not None and self.scan_thread.is_alive():
            self.after(100, self.check_scan_status)
        else:
            self.scan_thread = None
            if self.has_scanned: # scan successful
                self.master.master.master.enable_sidebar_links()
                self.desc_3.destroy()
                self.scan_button.destroy()
                self.cancel_scan_button.destroy()
                self.scan_pbar.destroy()
                self.scan_pbar_label_1.destroy()
                self.scan_pframe.destroy()
                self.scan_frame.destroy()
                self.has_scanned_display()
            else: # scan cancelled
                self.master.master.master.enable_sidebar_links()
                self.scan_button.pack(padx=12, pady=12, side="left")
                self.cancel_scan_button.destroy()
                self.scan_pbar.destroy()
                self.scan_pbar_label_1.destroy()
                self.scan_pframe.destroy()

    def cancel_scan(self):
        self.scan_cancel_flag.set()
        self.cancel_scan_button.configure(state="disabled", text="Cancelling...")
        self.after(100, self.check_scan_status)

    def add_label(self, address: str, label: str):
        print(f"NEW SENDER RULE CREATED > Email Address {address}'s emails will now be assigned label {label}")

        with open("src/data/sender_labels.json", "r") as file:
            data = json.load(file)
        try: data[label].append(address)
        except KeyError: data[label] = [address]
        with open("src/data/sender_labels.json", "w") as file:
            json.dump(data, file, indent=4)
        self.update_filter_dd()

    def update_filter_dd(self):
        with open("src/data/sender_labels.json", "r") as file:
            data = json.load(file)
        self.filter_label_dd.configure(values=list(data.keys()))

    def unsubscribe(self, address: str):
        print(f"NEW SENDER RULE CREATED > Email Address {address}'s emails will now be auto-trashed")

        if os.path.exists("src/data/unsubscribed.json"):
            with open("src/data/unsubscribed.json", "r") as file:
                data = json.load(file)
            data[address] = True
            with open("src/data/unsubscribed.json", "w") as file:
                json.dump(data, file, indent=4)
        else:
            with open("src/data/unsubscribed.json", "w") as file:
                json.dump({address: True}, file, indent=4)

    def resubscribe(self, address: str):
        print(f"SENDER RULE UPDATED > Email Address {address}'s emails will no longer be auto-trashed")

        if os.path.exists("src/data/unsubscribed.json"):
            with open("src/data/unsubscribed.json", "r") as file:
                data = json.load(file)
            del data[address]
            with open("src/data/unsubscribed.json", "w") as file:
                json.dump(data, file, indent=4)

    def delete_sender(self, pbar:ctk.CTkProgressBar, address: str):
        if self.delete_sender_thread is None or not self.delete_sender_thread.is_alive():
            print(f"SenderList 'DELETE' > Deleting sender {address} from the list and trashing all of their emails...")
            self.has_deleted_sender = False
            self.master.master.master.disable_sidebar_links()
            self.delete_sender_pbar = pbar
            self.delete_sender_address = address
            self.delete_sender_thread = threading.Thread(target=self.run_delete_sender, args=(address,))
            self.delete_sender_thread.start()
            self.after(100, self.check_delete_sender_status)
        else:
            print(f"SenderList 'DELETE' > A delete operation is already in progress")

    def check_delete_sender_status(self):
        if self.delete_sender_thread is not None and self.delete_sender_thread.is_alive():
            self.after(100, self.check_delete_sender_status)
        else:
            if self.has_deleted_sender:
                print(f"SenderList 'DELETE' > Deleted sender {self.delete_sender_address} from the list and trashed all of their emails")
                self.master.master.master.enable_sidebar_links()
                self.refresh_sender_list(self.delete_sender_address)
            else:
                print(f"SenderList 'DELETE' > Failed to delete sender {self.delete_sender_address}")
            self.delete_sender_thread = None
            self.delete_sender_address = None

    def run_delete_sender(self, address: str):
        try:
            rm_from_sender(address, self.update_delete_sender_progress)
            self.has_deleted_sender = True
        except Exception as e:
            print(f"Error deleting sender: {e}")
            self.has_deleted_sender = False

    def update_delete_sender_progress(self, progress):
        self.after(0, lambda: self.delete_sender_pbar.set(progress))

    def refresh_sender_list(self, address: str):
        if os.path.exists("src/data/senders.json"):
            with open("src/data/senders.json", "r") as file:
                data = json.load(file)
            
            if address in data: del data[address]

            with open("src/data/senders.json", "w") as file:
                json.dump(data, file, indent=4)

        self.senders = self.load_senders()
        self.sortedby = [None, None]

        self.after(0, self.display_senders)
        self.after(0, self.update_sort_buttons)

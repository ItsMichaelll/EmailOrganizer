import threading
import customtkinter as ctk

from src.GUI.AppStyles import *
from src.reset_inbox import remove_ai_organizer_labels, remove_standard_organizer_labels, reset_sender_labels, reset_unsubscribed_senders, reset_categories, reset_sender_list

class Settings(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            corner_radius=0,
            fg_color='transparent'
        )
        self.init_json_reset_buttons()
        self.init_organizer_reset_buttons()
        self.pack(padx=12, pady=12, fill="both")

    def init_json_reset_buttons(self):
        self.reset_buttons_frame = ctk.CTkFrame(
            master=self,
            fg_color=Level2PageFrameFG
        )
        self.reset_buttons_frame.columnconfigure(0, weight=0)
        self.reset_buttons_frame.columnconfigure(1, weight=1)
        self.reset_buttons_frame.columnconfigure(2, weight=0)
        self.reset_buttons_frame.rowconfigure(0, weight=0)
        self.reset_buttons_frame.rowconfigure(1, weight=0)
        self.reset_buttons_frame.rowconfigure(2, weight=0)
        self.reset_buttons_frame.rowconfigure(3, weight=0)

        self.reset_categories_lbl = ctk.CTkLabel(
            master=self.reset_buttons_frame,
            text="Clears the list of categories that you have created in 'AI Organizer'",
            font=("Switzer Medium", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.reset_categories_lbl.grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.reset_categories_btn = ctk.CTkButton(
            master=self.reset_buttons_frame,
            text="Reset Categories",
            font=("Switzer Semibold", 20),
            width=375,
            height=50,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.reset_categories,
        ); self.reset_categories_btn.grid(row=0, column=1, padx=(6,12), pady=12, sticky="w")
        
        self.reset_sender_labels_lbl = ctk.CTkLabel(
            master=self.reset_buttons_frame,
            text="Clears the list of senders that you have assigned labels in 'Sender List'",
            font=("Switzer Medium", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.reset_sender_labels_lbl.grid(row=1, column=0, padx=12, pady=12, sticky="w")
        self.reset_sender_labels_btn = ctk.CTkButton(
            master=self.reset_buttons_frame,
            text="Reset Sender Labels",
            font=("Switzer Semibold", 20),
            width=375,
            height=50,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.reset_sender_labels,
        ); self.reset_sender_labels_btn.grid(row=1, column=1, padx=(6,12), pady=12, sticky="w")

        self.reset_unsubscribed_lbl = ctk.CTkLabel(
            master=self.reset_buttons_frame,
            text="Clears the list of senders that you have unsubscribed from in 'Sender List'",
            font=("Switzer Medium", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.reset_unsubscribed_lbl.grid(row=2, column=0, padx=12, pady=12, sticky="w")
        self.reset_unsubscribed_btn = ctk.CTkButton(
            master=self.reset_buttons_frame,
            text="Reset Unsubscribed Senders",
            font=("Switzer Semibold", 20),
            width=375,
            height=50,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.reset_unsubscribed_senders,
        ); self.reset_unsubscribed_btn.grid(row=2, column=1, padx=(6,12), pady=12, sticky="w")

        self.reset_sender_list_lbl = ctk.CTkLabel(
            master=self.reset_buttons_frame,
            text="Clears the list of senders in 'Sender List'",
            font=("Switzer Medium", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.reset_sender_list_lbl.grid(row=3, column=0, padx=12, pady=12, sticky="w")
        self.reset_sender_list_btn = ctk.CTkButton(
            master=self.reset_buttons_frame,
            text="Reset Sender List",
            font=("Switzer Semibold", 20),
            width=375,
            height=50,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.reset_sender_list,
        ); self.reset_sender_list_btn.grid(row=3, column=1, padx=(6,12), pady=12, sticky="w")

        self.reset_buttons_frame.pack(padx=12, pady=12, fill="both")
    
    def reset_categories(self):
        print("Settings > Resetting Categories...")
        self.reset_categories_btn.configure(text="Clearing Categories...", fg_color=DARK_RED_HOVER)
        self.update()
        self.after(500)
        reset_categories()
        self.reset_categories_btn.configure(text="Categories Reset!")
        self.update()
        self.after(500, self.reset_categories_btn.configure(text="Reset Categories", fg_color=DARK_RED))
        print("Settings > Categories Reset!")

    def reset_sender_labels(self):
        print("Settings > Resetting Sender Labels...")
        self.reset_sender_labels_btn.configure(text="Clearing Sender Labels...", fg_color=DARK_RED_HOVER)
        self.update()
        self.after(500)
        reset_sender_labels()
        self.reset_sender_labels_btn.configure(text="Sender Labels Reset!")
        self.update()
        self.after(500, self.reset_sender_labels_btn.configure(text="Reset Sender Labels", fg_color=DARK_RED))
        print("Settings > Sender Labels Reset!")

    def reset_unsubscribed_senders(self):
        print("Settings > Resetting Unsubscribed Senders...")
        self.reset_unsubscribed_btn.configure(text="Clearing Unsubscribed Senders...", fg_color=DARK_RED_HOVER)
        self.update()
        self.after(500)
        reset_unsubscribed_senders()
        self.reset_unsubscribed_btn.configure(text="Unsubscribed Senders Reset!")
        self.update()
        self.after(500, self.reset_unsubscribed_btn.configure(text="Reset Unsubscribed Senders", fg_color=DARK_RED))
        print("Settings > Unsubscribed Senders Reset!")
    
    def reset_sender_list(self):
        print("Settings > Resetting Sender List...")
        self.reset_sender_list_btn.configure(text="Clearing Sender List...", fg_color=DARK_RED_HOVER)
        self.update()
        self.after(500)
        reset_sender_list()
        self.reset_sender_list_btn.configure(text="Sender List Reset!")
        self.update()
        self.after(500, self.reset_sender_list_btn.configure(text="Reset Sender List", fg_color=DARK_RED))
        print("Settings > Sender List Reset!")

    def init_organizer_reset_buttons(self):
        self.reset_organizer_frame = ctk.CTkFrame(
            master=self,
            fg_color=Level2PageFrameFG
        )
        self.reset_ai_organizer_frame = ctk.CTkFrame(
            master=self,
            fg_color=Level2PageFrameFG
        )
        self.reset_tip_frame = ctk.CTkScrollableFrame(
            master=self,
            fg_color=Level2PageFrameFG,
            height=0
        )

        self.reset_organizer_lbl = ctk.CTkLabel(
            master=self.reset_organizer_frame,
            text="Email Organizer Fresh Start:\nRemoves ALL labels assigned during the 'Standard Organizer' process from emails in your inbox",
            font=("Switzer Medium", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.reset_organizer_lbl.pack(padx=12, pady=12, fill="both")
        self.reset_organizer_btn = ctk.CTkButton(
            master=self.reset_organizer_frame,
            text="Email Organizer Fresh Start",
            font=("Switzer", 20, "bold"),
            width=375,
            height=50,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.reset_organizer,
        ); self.reset_organizer_btn.pack(padx=12, pady=12, side="left")
        self.reset_organizer_pbar = ctk.CTkProgressBar(
            master=self.reset_organizer_frame,
            width=500,
            height=25,
            progress_color=DARK_RED
        ); self.reset_organizer_frame.pack(padx=12, pady=12, fill="both")

        self.reset_ai_organizer_lbl = ctk.CTkLabel(
            master=self.reset_ai_organizer_frame,
            text="AI Organizer Fresh Start:\nRemoves ALL labels assigned during the 'AI Organizer' process from emails in your inbox",
            font=("Switzer Medium", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        ); self.reset_ai_organizer_lbl.pack(padx=12, pady=12, fill="both")
        self.reset_ai_organizer_btn = ctk.CTkButton(
            master=self.reset_ai_organizer_frame,
            text="AI Organizer Fresh Start",
            font=("Switzer", 20, "bold"),
            width=375,
            height=50,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            command=self.reset_ai_organizer,
        ); self.reset_ai_organizer_btn.pack(padx=12, pady=12, side="left")
        self.reset_ai_organizer_pbar = ctk.CTkProgressBar(
            master=self.reset_ai_organizer_frame,
            width=500,
            height=25,
            progress_color=DARK_RED
        ); self.reset_ai_organizer_frame.pack(padx=12, pady=12, fill="both")

        self.reset_tip_label = ctk.CTkLabel(
            master=self.reset_tip_frame,
            text="** Important Note: For the \"Fresh Start\" options, It's much faster for you to just go into your Gmail inbox and manually remove the labels. " \
                + "To do this, login to Gmail in a supported browser, hover over each of the labels under " \
                + "'Email Organizer/AI Organizer' and/or 'Email Organizer/Standard Organizer' and select the three dots that appear to the right " \
                + "of the label. From here, select the 'Remove Label' option. This will be much faster than the reset options here, and also won't leave behind any " \
                + "empty sub-labels.",
            font=("Switzer", 20, "italic"),
            wraplength=1000,
            justify="left",
            anchor="w"
        ); self.reset_tip_label.pack(padx=12, pady=12, fill="both")
        self.reset_tip_frame.pack(padx=12, pady=12, fill="both")

    def reset_organizer(self):
        print("Settings > Performing Email Organizer Fresh Start...")
        self.master.master.master.disable_sidebar_links()
        self.reset_organizer_btn.configure(state="disabled", fg_color=DARK_RED_HOVER, text="Resetting...")
        self.reset_organizer_pbar.set(0)
        self.reset_organizer_pbar.pack(padx=12, pady=(12.5, 12.5), side="left")

        self.reset_thread = threading.Thread(target=self.run_reset_organizer)
        self.reset_thread.start()
        self.after(100, self.check_reset_organizer_status)

    def reset_ai_organizer(self):
        print("Settings > Performing AI Organizer Fresh Start...")
        self.master.master.master.disable_sidebar_links()
        self.reset_ai_organizer_btn.configure(state="disabled", fg_color=DARK_RED_HOVER, text="Resetting...")
        self.reset_ai_organizer_pbar.set(0)
        self.reset_ai_organizer_pbar.pack(padx=12, pady=(12.5, 12.5), side="left")

        self.reset_ai_thread = threading.Thread(target=self.run_reset_ai_organizer)
        self.reset_ai_thread.start()
        self.after(100, self.check_reset_ai_organizer_status)

    def run_reset_organizer(self):
        remove_standard_organizer_labels(self.update_reset_organizer_pbar)

    def run_reset_ai_organizer(self):
        remove_ai_organizer_labels(self.update_reset_ai_organizer_pbar)

    def update_reset_organizer_pbar(self, progress, current, total, rate, elapsed):
        self.reset_organizer_pbar.set(progress)
        self.reset_organizer_btn.configure(text=f"Resetting... {current}/{total}")
        self.update()

    def update_reset_ai_organizer_pbar(self, progress, current, total, rate, elapsed):
        self.reset_ai_organizer_pbar.set(progress)
        self.reset_ai_organizer_btn.configure(text=f"Resetting... {current}/{total}")
        self.update()
    
    def check_reset_organizer_status(self):
        if self.reset_thread is not None and self.reset_thread.is_alive():
            self.after(100, self.check_reset_organizer_status)
        else:
            self.master.master.master.enable_sidebar_links()
            self.reset_organizer_pbar.pack_forget()
            self.update()
            self.reset_organizer_btn.configure(state="normal", text="Success!")
            self.update()
            self.after(500, self.reset_organizer_btn.configure(text="Email Organizer Fresh Start", fg_color=DARK_RED))
            print("Settings > Email Organizer Fresh Start Complete!")

    def check_reset_ai_organizer_status(self):
        if self.reset_ai_thread is not None and self.reset_ai_thread.is_alive():
            self.after(100, self.check_reset_ai_organizer_status)
        else:
            self.master.master.master.enable_sidebar_links()
            self.reset_ai_organizer_pbar.pack_forget()
            self.update()
            self.reset_ai_organizer_btn.configure(state="normal", text="Success!")
            self.update()
            self.after(500, self.reset_ai_organizer_btn.configure(text="AI Organizer Fresh Start", fg_color=DARK_RED))
            print("Settings > AI Organizer Fresh Start Complete!")

import customtkinter as ctk
from CTkListbox import CTkListbox
import os
import threading
import json

from PIL import Image

from ..ai_email_organizer import ai_email_organizer as ai_email_organizer
from .AppStyles import *

class AIOrganizer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            corner_radius=0,
            fg_color='transparent'
        )

        self.categories = self.load_categories()
        self.ai_organizer_thread = None
        self.ai_organizer_flag = threading.Event()

        self.create_widgets()
        self.pack(padx=12, pady=12, side="right", fill="both", expand=True)

    def create_widgets(self):
        self.create_description_labels()
        self.create_feedback_frame()
        self.create_edit_categories_frame()
        self.create_categories_frame()
        self.create_ai_organizer_frame()

    def create_description_labels(self):
        self.desc_1 = ctk.CTkLabel(
            master=self,
            text="Below, you can use Gmail labels and AI to organize your inbox into categories. You can...",
            font=("Switzer Semibold", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        )
        self.desc_1.pack(padx=12, pady=12, fill="x")

        self.desc_2 = ctk.CTkLabel(
            master=self,
            text="• Manage a list of categories that you would like your inbox to be sorted into\n\n" \
                + "• Have our AI Organizer scan your emails and sort them into the categories you've created\n\n" \
                + "• Choose between organizing ALL of your emails at once or a select amount of emails," \
                + " starting from the oldest email that our AI organizer hasn't sorted yet\n\n" \
                + "• Cancel the AI Organizer at any time to kill the process",
            font=("Switzer", 20),
            wraplength=1000,
            justify="left",
            anchor="w",
        )
        self.desc_2.pack(padx=12, pady=12, fill="x")

    def create_categories_frame(self):
        self.frame1 = ctk.CTkFrame(master=self, corner_radius=0, fg_color=Level2PageFrameFG)
        self.frame1.pack(padx=12, pady=12, fill="both", expand=True)

        self.categories_listbox = self.add_categories_list()
        self.categories_listbox.pack(padx=12, pady=12, side="top", fill="both", expand=True)

    def create_feedback_frame(self):
        self.frame2 = ctk.CTkFrame(master=self, corner_radius=0, fg_color=Level2PageFrameFG)
        self.frame2.pack(padx=12, pady=(12, 0), fill="x")

        self.feedback_label = ctk.CTkLabel(
            master=self.frame2,
            text="",
            text_color="#FFF",
            font=("Switzer Semibold", 18),
            anchor="w",
        )
        self.feedback_label.pack(padx=14, pady=6, fill="x")

    def create_edit_categories_frame(self):
        self.frame3 = ctk.CTkFrame(master=self, fg_color="transparent")
        self.frame3.pack(padx=0, pady=12, fill="x")

        self.edit_categories_label = ctk.CTkLabel(
            master=self.frame3,
            text="Manage your categories",
            font=("Switzer", 18, "bold"),
            anchor="w",
        )
        self.edit_categories_label.pack(padx=12, pady=(0, 10), fill="x")

        self.category_entry = ctk.CTkEntry(
            master=self.frame3,
            width=300,
            height=45,
            placeholder_text="Enter a category name",
            font=("Switzer", 18, "bold"),
            border_width=0,
            fg_color=Level2PageFrameFG,
            corner_radius=0
        )
        self.category_entry.pack(padx=(12,0), pady=0, side="left", fill="x")
        self.category_entry.bind("<Return>", lambda e: self.add_category())

        self.add_category_button = ctk.CTkButton(
            master=self.frame3,
            width=200,
            height=45,
            text="Add Category",
            font=("Switzer", 18, "bold"),
            fg_color=DARK_BLUE_HOVER,
            hover_color=DARK_BLUE,
            corner_radius=0,
            command=self.add_category,
        )
        self.add_category_button.pack(padx=0, pady=0, side="left", fill="x")

        self.create_remove_category_button()

    def create_remove_category_button(self):
        self.trash_icon = ctk.CTkImage(
            light_image=Image.open("src/assets/trashbin (light).png"),
            dark_image=Image.open("src/assets/trashbin (light).png"),
            size=(32, 32),
        )

        self.remove_category_button = ctk.CTkButton(
            master=self.frame3,
            width=125,
            height=45,
            fg_color=DARK_RED,
            hover_color=DARK_RED_HOVER,
            image=self.trash_icon,
            text="Remove Selected Categories",
            font=("Switzer", 18, "bold"),
            command=self.remove_category
        )
        self.remove_category_button.pack(padx=(10, 0), pady=0, side="left", fill="x")
        self.remove_category_button.bind("<Delete>", lambda e: self.remove_category)

    def create_ai_organizer_frame(self):
        self.frame4 = ctk.CTkFrame(master=self, fg_color="transparent")
        self.frame4.pack(padx=0, pady=12, fill="x")

        self.ai_organizer_label = ctk.CTkLabel(
            master=self.frame4,
            text="AI Organizer Settings",
            font=("Switzer", 18, "bold"),
            anchor="w",
        )
        self.ai_organizer_label.pack(padx=10, pady=0, fill="x")

        self.create_ai_organizer_settings()

    def create_ai_organizer_settings(self):
        self.frame5 = ctk.CTkFrame(master=self.frame4, fg_color="transparent")
        self.frame5.pack(padx=0, pady=6, fill="x")

        self.switch_var = ctk.StringVar(value="on")
        self.organize_all_switch = ctk.CTkSwitch(
            master=self.frame5,
            switch_width=50,
            switch_height=25,
            text="Organize ALL of the emails in your inbox",
            font=("Switzer", 18, "bold"),
            progress_color=DARK_BLUE_HOVER,
            command=self.switch_organize_all,
            button_color = ['#2c2c2c', '#c6c9d2'],
            button_hover_color = ['#000', '#FFF'],
            variable=self.switch_var,
            onvalue="on",
            offvalue="off"
        )
        self.organize_all_switch.pack(padx=10, pady=6, side="left")

        self.num_emails_entry = ctk.CTkEntry(
            master=self.frame5,
            width=150,
            height=40,
            font=("Switzer", 18, "bold"),
            corner_radius=0,
            fg_color=Level2PageFrameFG,
            border_width=0
        )
        self.num_emails_entry.pack(padx=10, pady=6, side="left")
        self.num_emails_entry.insert(0, "ALL")
        self.num_emails_entry.configure(state="readonly")

        self.organize_button = ctk.CTkButton(
            master=self.frame5,
            width=200,
            height=40,
            text="Start AI Organizer",
            font=("Switzer", 18, "bold"),
            fg_color=DARK_BLUE_HOVER,
            hover_color=DARK_BLUE,
            command=self.organize_inbox,
        )
        self.organize_button.pack(padx=10, pady=6, side="left")

        self.cancel_button = ctk.CTkButton(
            master=self.frame5,
            width=200,
            height=40,
            text="Cancel AI Organizer",
            font=("Switzer", 18, "bold"),
            fg_color='#bd170b',
            hover_color='#590600',
            command=self.cancel_organize,
        )

    def add_categories_list(self):
        categories_list = CTkListbox(
            master=self.frame1,
            height=100,
            text_color=['#000', '#FFF'],
            font=("Switzer Semibold", 18),
            fg_color=Level2PageFrameFG,
            bg_color="transparent",
            hover_color=DARK_BLUE,
            highlight_color=DARK_BLUE_HOVER,
            border_width=0,
            multiple_selection=True
        )
        for category in self.categories:
            categories_list.insert("end", category)
        return categories_list

    def load_categories(self):
        if os.path.exists("src/data/data.json"):
            with open("src/data/data.json", "r") as file:
                data = json.load(file)
                return data.get("categories", [])
        else:
            return []
    
    def save_categories(self):
        with open("src/data/data.json", "w") as file:
            json.dump({"categories": self.categories}, file, indent=4)

    def add_category(self):
        category_name = self.category_entry.get()

        if category_name in set(self.categories):
            self.feedback_label.configure(
                text=f"Error: Category '{category_name}' already exists!",
                text_color=FeedbackLabelErrorColor,
            )
            return
        elif category_name == "":
            self.feedback_label.configure(
                text="Error: Category name cannot be empty!", text_color=FeedbackLabelErrorColor
            )
            return
        else:
            self.categories.append(category_name)
            self.categories_listbox.insert("end", category_name)
            self.category_entry.delete(0, "end")
            self.save_categories()
            self.feedback_label.configure(
                text=f"Category '{category_name}' added successfully!",
                text_color=FeedbackLabelSuccessColor,
            )

    def remove_category(self):
        indices = self.categories_listbox.curselection()

        if len(indices) == 0:
            feedback_text = "No category selected! Please select a category to delete."
            self.feedback_label.configure(text=feedback_text, text_color=FeedbackLabelErrorColor)
            return
        elif len(indices) > 1:
            n_removed = 0
            for i in indices:
                category_name = self.categories_listbox.get(i-n_removed)
                self.categories_listbox.delete(i-n_removed)
                self.categories.remove(category_name)
                n_removed += 1
            feedback_text = f"Successfully removed {n_removed} categories."
            self.feedback_label.configure(text=feedback_text, text_color=FeedbackLabelSuccessColor)
        elif len(indices) == 1:
            i = indices[0]
            category_name = self.categories_listbox.get(i)
            self.categories_listbox.delete(i)
            self.categories.remove(category_name)
            feedback_text = f"Category '{category_name}' removed successfully."
            self.feedback_label.configure(text=feedback_text, text_color=FeedbackLabelSuccessColor) 
        
        self.save_categories()

    def switch_organize_all(self):
        if self.switch_var.get() == "on":
            self.num_emails_entry.delete(0, "end")
            self.num_emails_entry.insert(0, "ALL")
            self.num_emails_entry.configure(state="readonly")
            self.organize_all_switch.configure(text="Organize ALL of the emails in your inbox")
        else:
            self.num_emails_entry.configure(state="normal")
            self.num_emails_entry.delete(0, "end")
            self.num_emails_entry.configure(placeholder_text="# of emails")
            self.organize_all_switch.configure(text="Organize specific amount of emails")
            self.num_emails_entry.unbind_class

    def organize_inbox(self):
        if self.switch_var.get() == "on":
            num_emails = "all"
        else:
            try:
                num_emails = int(self.num_emails_entry.get())
            except ValueError:
                self.feedback_label.configure(
                    text="Error: Please specify the amount of emails to organize, or switch to 'Organize ALL'",
                    text_color=FeedbackLabelErrorColor
                )
                return
        
        # if no categories
        if len(self.categories) == 0:
            self.feedback_label.configure(
                text="Error: No categories found. Please add a few categories before organizing your inbox.",
                text_color=FeedbackLabelErrorColor
            )
            return

        self.save_categories()
        self.feedback_label.configure(
            text="AI Organizer started. Please wait, this may take some time...",
            text_color=FeedbackLabelPendingColor
        )

        self.ai_organizer_flag.clear()
        self.ai_organizer_thread = threading.Thread(
            target=self.run_ai_organizer,
            args=(num_emails,)
        )
        self.ai_organizer_thread.start()
        self.organize_button.pack_forget()
        self.cancel_button.pack(padx=10, pady=6, side="left")

        self.after(100, self.check_thread_status)

    def check_thread_status(self):
        if self.ai_organizer_thread is not None and self.ai_organizer_thread.is_alive():
            self.ai_organizer_thread = None
            if self.ai_organizer_flag.is_set():
                self.feedback_label.configure(
                    text="Inbox organization cancelled.",
                    text_color=FeedbackLabelErrorColor
                )
            else:
                pass
        else:
            self.after(500, self.check_thread_status)

    def run_ai_organizer(self, num_emails):
        self.master.master.master.disable_sidebar_links()

        try:
            result = ai_email_organizer(self.ai_organizer_flag, num_emails)
        except Exception as e:
            self.feedback_label.configure(
                text="Error: AI Organizer encountered an error.",
                text_color=FeedbackLabelErrorColor
            )
            print(e)

        if result == "SUCCESS":
            self.feedback_label.configure(
                text="Inbox organized successfully!",
                text_color=FeedbackLabelSuccessColor
            )
        elif result == "CANCELLED":
            self.feedback_label.configure(
                text="Inbox organization cancelled.",
                text_color=FeedbackLabelErrorColor
            )
        elif result == "ERROR":
            self.feedback_label.configure(
                text="Error: AI Organizer encountered an error.",
                text_color=FeedbackLabelErrorColor
            )

        self.cancel_button.pack_forget()
        self.organize_button.pack(padx=10, pady=0, side="left", fill="x")
        self.master.master.master.enable_sidebar_links()

    def cancel_organize(self):
        self.ai_organizer_flag.set()
        self.feedback_label.configure(
            text="Cancelling...",
            text_color=FeedbackLabelPendingColor
        )
        self.cancel_button.pack_forget()
        self.organize_button.pack(padx=10, pady=6, side="left")

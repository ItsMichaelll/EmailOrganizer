import customtkinter as ctk

from PIL import Image
from .EmailOrganizer import EmailOrganizer
from .AIOrganizer import AIOrganizer
from .SenderList import SenderList
from .Settings import Settings

from .AppStyles import *

START_PAGE = "Email Organizer"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Email Organizer")
        self.minsize(1400, 850)
        self.current_page = START_PAGE
        self.appearance = "Dark"
        
        self.bind_all("<Button>", self.change_focus)
        
        self.header = HeaderFrame(master=self)
        self.sidebar_toggle = SidebarToggle(master=self.header)
        self.title_frame = TitleFrame(master=self.header) 

        self.body_frame = BodyFrame(master=self)
        self.sidebar = Sidebar(master=self.body_frame)
        self.page_frame = PageFrame(master=self.body_frame)

    def get_current_page(self):
        return self.current_page
    
    def set_current_page(self, page):
        self.update()
        self.current_page = page
        self.page_frame.change_page(page)
        self.update()
    
    def toggle_day_night(self):
        self.update()
        self.appearance = "Light" if self.appearance == "Dark" else "Dark"
        ctk.set_appearance_mode("light" if self.appearance == "Light" else "dark")
        self.update()

    def change_focus(self, event):
        try: event.widget.focus_set()
        except AttributeError: pass

    def disable_sidebar_links(self):
        self.sidebar.disable_links()
    
    def enable_sidebar_links(self):
        self.sidebar.enable_links()

class HeaderFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            width=500,
            height=200,
            corner_radius=0,
            fg_color=HeaderFrameFG,
        ); self.pack(fill="x")

class SidebarToggle(ctk.CTkButton):
    def __init__(self, master):
        self.sidebar_toggle_frame = ctk.CTkFrame(
            master=master,
            width=250,
            fg_color=SidebarToggleFrameFG,
        ); self.sidebar_toggle_frame.pack(padx=86, pady=0, side="left", fill="both")
        super().__init__(
            master=self.sidebar_toggle_frame,
            text="",
            width=50,
            image=ctk.CTkImage(
                light_image=Image.open("src/assets/sidebar (black).png"),
                dark_image=Image.open("src/assets/sidebar (white).png"),
                size=(64, 64)),
            bg_color="transparent",
            fg_color=SidebarToggleBtnFg,
            hover_color=SidebarToggleHover,
            command=self.toggle_sidebar)
        self.pack(padx=10, pady=12, side="left", fill="both")
        self.sidebar_on = True

    def toggle_sidebar(self):
        if self.sidebar_on:
            self.master.master.master.sidebar.pack_forget()
            self.sidebar_on = False
        else:
            self.master.master.master.sidebar.pack(
                ipady=12, side="left", fill="y",
                before=self.master.master.master.page_frame)
            self.sidebar_on = True

class TitleFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            height=300,
            corner_radius=0,
            fg_color=TitleFrameFG,
        ); self.pack(padx=0, pady=0, fill="both")

        self.title_label = ctk.CTkLabel(
            master=self,
            text=TitleLabel,
            font=TitleLabelFont,
            text_color=TitleLabelColor,
            compound="left",
            anchor="w"
        )
        self.title_label.pack(padx=0, pady=(12, 0), side="top")

        self.desc_label = ctk.CTkLabel(
            master=self,
            text=TitleDescLabel,
            font=TitleDescLabelFont,
            text_color=TitleDescLabelColor,
            compound="left",
        )
        self.desc_label.pack(padx=0, pady=(0,12), side="bottom")

class BodyFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            corner_radius=0,
            fg_color=BodyFrameFG,
        ); self.pack(padx=0, pady=0, fill="both", expand=True)

class Sidebar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            width=250,
            corner_radius=0,
            fg_color=SidebarFrameFG,
        ); self.pack(side="left", fill="both")
        
        self.pages = []
        self.page_info = {
            "Email Organizer": {"icon": "src/assets/Email Organizer Icon.png", "command": self.show_organizer},
            "AI Organizer": {"icon": "src/assets/AI Email Organizer Icon.png", "command": self.show_ai_organizer},
            "Sender List": {"icon": "src/assets/Senders Icon.png", "command": self.show_senderlist},
            "Settings": {"icon": "src/assets/settings.png", "command": self.show_settings}
        }

        for page_name, info in self.page_info.items():
            self.add_page_link(page_name, info["icon"], info["command"])
        
        for page in self.pages: 
            page.pack(padx=10, pady=(0,12), fill="x")
        
        self.day_night_toggle = self.add_day_night_switch()
        self.day_night_toggle.pack(padx=20, pady=12, side="bottom", fill="both")

    def add_page_link(self, page_name, page_icon, command):
        icon = ctk.CTkImage(
            light_image=Image.open(page_icon),
            dark_image=Image.open(page_icon),
            size=(96,96)
        )

        button = ctk.CTkButton(
            master=self,
            width=225,
            height=45,
            image=icon,
            text=page_name,
            font=SidebarLinkFont,
            text_color=SidebarLinkTextColor,
            bg_color="transparent",
            fg_color=SidebarLinkFG,
            hover_color=SidebarLinkHover,
            anchor="w",
            command=command
        )

        self.pages += [button]

    def get_current_page(self):
        return self.master.master.get_current_page()

    def set_current_page(self, page):
        self.master.master.set_current_page(page)

    def show_organizer(self):
        if self.get_current_page() == "Email Organizer": return
        self.set_current_page("Email Organizer")

    def show_ai_organizer(self):
        if self.get_current_page() == "AI Organizer": return
        self.set_current_page("AI Organizer")

    def show_senderlist(self):
        if self.get_current_page() == "Sender List": return
        self.set_current_page("Sender List")
    
    def show_settings(self):
        if self.get_current_page() == "Settings": return
        self.set_current_page("Settings")

    def add_day_night_switch(self):
        icon = ctk.CTkImage(
                light_image=Image.open("src/assets/sun.png"),
                dark_image=Image.open("src/assets/moon.png"),
                size=(64, 64))
        
        return ctk.CTkButton(
            master=self,
            text="Dark Mode",
            width=175,
            image=icon,
            font=DayNightBtnFont,
            fg_color=DayNightBtnFG,
            hover_color=DayNightBtnHover,
            bg_color="transparent",
            anchor="w",
            corner_radius=DayNightBtnCornerRadius,
            border_spacing=5,
            text_color=DayNightBtnTextColor,
            command=self.toggle_day_night,
        )

    def toggle_day_night(self):
        self.master.master.toggle_day_night()
        text = f"{self.master.master.appearance} Mode"
        self.day_night_toggle.configure(text=text)

    def disable_links(self):
        for link in self.pages:
            link.configure(state="disabled")
    
    def enable_links(self):
        for link in self.pages:
            link.configure(state="normal")

class PageFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master=master,
            corner_radius=0,
            fg_color=PageFrameFG
        )
        self.pack(padx=0, pady=0, fill="both", expand=True)
        self.current_page = START_PAGE
        self.pages = {
            "Email Organizer": EmailOrganizer,
            "AI Organizer": AIOrganizer,
            "Sender List": SenderList,
            "Settings": Settings
        }
        self.page = self.pages[self.current_page](master=self)

    def change_page(self, new_page):
        if new_page not in self.pages:
            raise ValueError(f"Invalid page name: {new_page}")
        
        self.current_page = new_page
        self.page.pack_forget()
        self.page = self.pages[self.current_page](master=self)

if __name__ == "__main__":
    app = App()
    app.mainloop()

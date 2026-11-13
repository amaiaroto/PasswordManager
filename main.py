import threading
import tkinter as tk
from typing import Literal

from AuthObject import *


class States(Enum):
    main = "MAIN_PASSWORD_ENTRY_SCREEN"
    main_password_not_entered = "MAIN_MASTER_PASS_NOT_ENTERED_EVENT"
    main_password_entered = "MAIN_MASTER_PASS_ENTERED_EVENT"
    sign_in = "SIGNED_IN_WITH_PASSWORD_SELECT_SCREEN"
    password_unselected = "PASSWORD_NOT_SELECTED_EVENT"
    password_selected = "PASSWORD_SELECTED_EVENT"


class PasswordManager:
    def __init__(self, window_name, window_size=None, **kwargs):
        self.root = tk.Tk()

        if window_size is not None:
            self.root.geometry(window_size)

        with open("configs.json") as configs:
            self.configs = json.loads(configs.read())

        self.state: Literal[
            States.main,
            States.sign_in
        ] = States.main
        self.event_state: Literal[
            States.main_password_entered,
            States.password_unselected,
            States.password_selected,
            States.main_password_not_entered
        ] = States.main_password_not_entered

        self.root.title(window_name)

        self.main_title = tk.Label(self.root)
        self.main_title.configure(text="Enter Password", font=self.configs['Fonts']['Title'])
        self.main_title_settings = self.configs['Places']['Title']

        self.master_password_box = tk.Entry(self.root)
        self.master_password_box.configure(width=19, font=self.configs['Fonts']['Password Box'])
        self.master_password_box_settings = self.configs['Places']['Password Box']

        self.submit_button = tk.Button(self.root)
        self.submit_button.configure(text="Submit",
                                     bg="green", activebackground="light green",
                                     width=12, font=self.configs['Fonts']['Submit Button'],
                                     command=lambda: self.check_password(self.master_password_box.get()))
        self.submit_button_settings = self.configs['Places']['Submit Button']

        self.show = False
        self.show_button_packed = False

        self.site_info_frame = tk.Frame(self.root)
        self.site_info_frame.configure(borderwidth=5, relief="raised", width=50, height=8)
        self.site_info_frame_settings = self.configs['Places']['Web Info Frame']

        self.site_list_frame = tk.Frame(self.root)
        self.site_list_frame.configure(borderwidth=5, relief="raised", width=50, height=35)
        self.site_list_frame_settings = self.configs['Places']['Web List Frame']

        self.site_info = tk.Label(self.site_info_frame)
        self.site_info.configure(font=self.configs['Fonts']['Web Info'],
                                 text="You haven't selected anything yet.\nSelect a website to view its properties.",
                                 width=50, height=7)
        self.site_info_settings = self.configs['Places']['Site Info']

        self.show_button = tk.Checkbutton(self.site_info_frame)
        self.show_button.configure(text="Show", command=self.show_password_toggle)
        self.show_button_settings = self.configs['Places']['Show Button']

        self.site_list = kwargs["websites"]

        self.site_listbox = tk.Listbox(self.site_list_frame, height=13, width=40)
        self.web_scrollbar = tk.Scrollbar(self.site_list_frame, orient='vertical')

        self.site_listbox.configure(yscrollcommand=self.web_scrollbar.set)
        self.web_scrollbar.configure(command=self.site_listbox.yview)

        self.site_listbox_settings = self.configs['Places']['Web Listbox']
        self.web_scrollbar_settings = self.configs['Places']['Web Scrollbar']

        # self.web_name = tk.Label()
        # self.web_name_settings = self.configs['Places']['Web Title']
        # TODO add site title like example.com\nblah

        self.running: bool = True

    def password_show_check(self):
        selected = self.site_listbox.curselection()

        self.site_info.config(
            text=f"Username: {self.site_list[selected[0]].username}\nPassword: "
                 f"{self.site_list[selected[0]].password if self.show else "*" * len(self.site_list[selected[0]].password)}")

    def show_password_toggle(self):
        if not self.show_button_packed:
            self.show_button.pack(**self.show_button_settings)
            self.show_button_packed = True

        else:
            self.show_button.pack_forget()
            self.show_button_packed = False

        self.show = not self.show
        self.password_show_check()

    def check_password(self, password):
        if password == 'aaa':
            self.main_title.configure(text="Password Manager")
            self.master_password_box.place_forget()
            self.submit_button.place_forget()
            self.state = States.sign_in

    def state_display(self):
        while self.running:
            if self.state == States.main:
                if self.master_password_box.get():
                    self.event_state = States.main_password_entered

                else:
                    self.event_state = States.main_password_not_entered

            if self.state == States.sign_in:
                if self.site_listbox.curselection():
                    self.event_state = States.password_selected

                else:
                    self.event_state = States.password_unselected

            match self.state, self.event_state:
                case States.main, (States.main_password_entered | States.main_password_not_entered):
                    self.main_title.place(**self.main_title_settings)
                    self.master_password_box.place(**self.master_password_box_settings)
                    self.submit_button.place(**self.submit_button_settings)

                case States.main, States.main_password_not_entered:
                    self.submit_button['state'] = 'disabled'

                case States.main, States.main_password_entered:
                    self.submit_button['state'] = 'normal'

                case States.sign_in, (States.password_unselected | States.password_selected):
                    self.site_info_frame.place(**self.site_info_frame_settings)
                    self.site_info.pack(**self.site_info_settings)
                    self.site_list_frame.place(**self.site_list_frame_settings)
                    self.site_listbox.pack(**self.site_listbox_settings)

                    for s in range(len(self.site_list)):
                        self.site_listbox.insert(s, self.site_list[s].url)

                case States.sign_in, States.password_unselected:
                    self.show_button.pack_forget()
                    self.show_button_packed = False
                    self.password_show_check()

                case States.sign_in, States.password_selected:
                    self.show_button.pack(**self.show_button_settings)
                    self.show_button_packed = True
                    self.password_show_check()

    def main(self):
        display_thread = threading.Thread(target=self.state_display)
        display_thread.start()

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        self.root.geometry(f'{int(sw // 1.2 if sw > 1250 else sw)}x{int(sh // 1.25 if sh > 850 else sh)}')
        self.root.mainloop()


# websites = vault
# site_info: tk.Label
# site_info_frame: tk.Frame
# packed = False
#
#
# def select_site(event):
#     global site_info, websites, site_info_frame, packed
#
#     def show_password():
#         nonlocal show, selected
#         global site_info, websites
#
#         show = not show
#         site_info.config(
#             text=f"Username: {websites[selected[0]].username}\nPassword: "
#                  f"{websites[selected[0]].password if show else "*" * len(websites[selected[0]].password)}"
#         )
#
#     sites: tk.Listbox = event.widget
#     selected = sites.curselection()
#     show = False
#
#     site_info.config(
#         text=f"Username: {websites[selected[0]].username}\nPassword: "
#              f"{websites[selected[0]].password if show else "*" * len(websites[selected[0]].password)}")
#
#     show_button = tk.Checkbutton(site_info_frame)
#     show_button.config(text="Show", command=show_password)
#
#     if not packed:
#         show_button.pack()
#         packed = True
#
#
# def signed_in():
#     global root, websites, configs, site_info, site_info_frame
#
#     root.title("Password Manager \u2014 Signed In")
#     site_info_frame = tk.Frame(root)
#     site_info_frame.config(borderwidth=5, relief="raised", width=50, height=8)
#     site_info_frame.place(**configs['Places']['Web Info Frame'])
#     site_list_frame = tk.Frame(root)
#     site_list_frame.config(borderwidth=5, relief="raised", width=50, height=35)
#     site_list_frame.place(**configs['Places']['Web List Frame'])
#     site_info = tk.Label(site_info_frame)
#     site_info.config(font=configs['Fonts']['Web Info'],
#                      text="You haven't selected anything yet.\nSelect a website to view its data.",
#                      width=50, height=7)
#     site_info.pack()
#     sites = tk.Listbox(site_list_frame, height=13, width=40)
#     web_scrollbar = tk.Scrollbar(site_list_frame, orient='vertical')
#     sites.config(yscrollcommand=web_scrollbar.set)
#     web_scrollbar.config(command=sites.yview)
#
#     for s in range(len(websites)):
#         sites.insert(s, websites[s].url)
#
#     sites.bind("<<ListboxSelect>>", select_site)
#     web_scrollbar.pack(side="right", fill="y")
#     sites.pack(side='left', fill='y')
#
#
# def check_password(password):
#     global title, master_password_box, submit_password_button
#
#     if password == 'aaa':
#         title.config(text="Password Manager")
#         master_password_box.destroy()
#         submit_password_button.destroy()
#         signed_in()
#
#
# def enter_pressed(event):
#     global master_password_box
#
#     if event.widget == master_password_box:
#         check_password(event.widget.get())


# https://stackoverflow.com/questions/27820178/how-to-add-placeholder-to-an-entry-in-tkinter
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self['show'] = "\u2022"
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self['show'] = None
            self.put_placeholder()


# root = tk.Tk()
#
# sh = root.winfo_screenheight()
# sw = root.winfo_screenwidth()
#
# s = f'{int(sw // 1.2 if sw > 1250 else sw)}x{int(sh // 1.25 if sh > 850 else sh)}'
# root.quit()
# root.geometry(s)

# title = tk.Label(root)
# title.config(text="Enter Password", font=configs['Fonts']['Title'])
# title.place(**configs['Places']['Title'])
#
# master_password_box = PlaceholderEntry(root, "Enter password...")
# master_password_box.config(width=19, font=configs['Fonts']['Password Box'])
# root.bind("<Return>", enter_pressed)
# master_password_box.place(**configs['Places']['Password Box'])
#
# submit_password_button = tk.Button()
# submit_password_button.config(
#     text="Submit",
#     bg="green", activebackground="light green",
#     width=12, font=configs['Fonts']['Submit Button'],
#     command=lambda: check_password(master_password_box.get())
# )
# submit_password_button.place(**configs['Places']['Submit Button'])
#
# root.title("Password Manager")
# root.wm_iconphoto(True, "pm_icon.png")
pm = PasswordManager("Password Manager", websites=vault)
pm.main()

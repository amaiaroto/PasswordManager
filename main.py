import tkinter as tk

from AuthObject import *


class PasswordManager:
    def __init__(self, window_name, window_size, **kwargs):
        with open("configs.json") as configs:
            self.configs = json.loads(configs.read())

        self.root = tk.Tk()

        self.root.title(window_name)
        self.root.geometry(window_size)

        self.main_title = tk.Label(self.root)
        self.main_title.configure(text="Enter Password", font=self.configs['Fonts']['Title'])


websites = vault
site_info: tk.Label
site_info_frame: tk.Frame
packed = False


def select_site(event):
    global site_info, websites, site_info_frame, packed

    def show_password():
        nonlocal show, selected
        global site_info, websites

        show = not show
        site_info.config(
            text=f"Username: {websites[selected[0]].username}\nPassword: "
                 f"{websites[selected[0]].password if show else "*" * len(websites[selected[0]].password)}"
        )

    sites: tk.Listbox = event.widget
    selected = sites.curselection()
    show = False

    site_info.config(
        text=f"Username: {websites[selected[0]].username}\nPassword: "
             f"{websites[selected[0]].password if show else "*" * len(websites[selected[0]].password)}")

    show_button = tk.Checkbutton(site_info_frame)
    show_button.config(text="Show", command=show_password)

    if not packed:
        show_button.pack()
        packed = True


def signed_in():
    global root, websites, configs, site_info, site_info_frame

    root.title("Password Manager \u2014 Signed In")
    site_info_frame = tk.Frame(root)
    site_info_frame.config(borderwidth=5, relief="raised", width=50, height=8)
    site_info_frame.place(**configs['Places']['Web Info Frame'])
    site_list_frame = tk.Frame(root)
    site_list_frame.config(borderwidth=5, relief="raised", width=50, height=35)
    site_list_frame.place(**configs['Places']['Web List Frame'])
    site_info = tk.Label(site_info_frame)
    site_info.config(font=configs['Fonts']['Web Info'],
                     text="You haven't selected anything yet.\nSelect a website to view its data.",
                     width=50, height=7)
    site_info.pack()
    sites = tk.Listbox(site_list_frame, height=13, width=40)
    web_scrollbar = tk.Scrollbar(site_list_frame, orient='vertical')
    sites.config(yscrollcommand=web_scrollbar.set)
    web_scrollbar.config(command=sites.yview)

    for s in range(len(websites)):
        sites.insert(s, websites[s].url)

    sites.bind("<<ListboxSelect>>", select_site)
    web_scrollbar.pack(side="right", fill="y")
    sites.pack(side='left', fill='y')


def check_password(password):
    global title, master_password_box, submit_password_button

    if password == 'aaa':
        title.config(text="Password Manager")
        master_password_box.destroy()
        submit_password_button.destroy()
        signed_in()


def enter_pressed(event):
    global master_password_box

    if event.widget == master_password_box:
        check_password(event.widget.get())


# https://stackoverflow.com/questions/27820178/how-to-add-placeholder-to-an-entry-in-tkinter
class PlaceholderEntry(tk.Entry):
    global configs

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


root = tk.Tk()

sh = root.winfo_screenheight()
sw = root.winfo_screenwidth()

s = f'{int(sw // 1.2 if sw > 1250 else sw)}x{int(sh // 1.25 if sh > 850 else sh)}'
root.geometry(s)

title = tk.Label(root)
title.config(text="Enter Password", font=configs['Fonts']['Title'])
title.place(**configs['Places']['Title'])

master_password_box = PlaceholderEntry(root, "Enter password...")
master_password_box.config(width=19, font=configs['Fonts']['Password Box'])
root.bind("<Return>", enter_pressed)
master_password_box.place(**configs['Places']['Password Box'])

submit_password_button = tk.Button()
submit_password_button.config(
    text="Submit",
    bg="green", activebackground="light green",
    width=12, font=configs['Fonts']['Submit Button'],
    command=lambda: check_password(master_password_box.get())
)
submit_password_button.place(**configs['Places']['Submit Button'])

root.title("Password Manager")
# root.wm_iconphoto(True, "pm_icon.png")
root.mainloop()

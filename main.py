import os
import tkinter as tk
from AuthObject import *
# from PIL import Image, ImageTk
# import tkFileDialog

# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
#
# def decrypt_file(name: str):
#     with open(name, 'rb') as data:
#         data = data.read()
#
#     return data
#
# password = b"1234"
# kdf = Argon2id(length=32, iterations=1, lanes=4, memory_cost=2 ** 21, salt=os.urandom(16))
# key = base64.urlsafe_b64encode(kdf.derive(password))
# f = Fernet(key)
# token = f.encrypt(password)

# print(token)
# print(f.decrypt(token))

with open("configs.json") as configs:
    configs = json.loads(configs.read())


websites = ["google.com", "stackoverflow.com"]

def signed_in():
    global root, websites, configs

    root.title("Password Manager \u2014 Signed In")

    sites = tk.Listbox(root)
    sites.place(**configs['Places']['Web List'])

    web_scrollbar = tk.Scrollbar(root)
    sites.config()
    web_scrollbar.config(command=sites.yview)

    sites.config()

    for s in range(len(websites)):
        sites.insert(s, websites[s])

    sites.bind("<<ListboxSelect>>", )


def check_password(password):
    global title, master_password_box, submit_password_button

    if password == 'abc':
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

# path = tkFileDialog.askopenfilename(filetypes=[("Image File", '.jpg', '.png', '.webp')])
# im = Image.open(path)
# tkimage = ImageTk.PhotoImage(im)
# myvar = tk.Label(root, image=tkimage)
# myvar.image = tkimage

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
submit_password_button.place(**configs['Place']['Submit Button'])

root.title("Password Manager")
# root.wm_iconphoto(True, "pm_icon.png")
root.mainloop()

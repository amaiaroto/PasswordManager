import tkinter as tk

from AuthObject import *


class States(Enum):
    main = "MAIN_PASSWORD_ENTRY_SCREEN"
    main_password_entered = "MAIN_ENTER_PASSWORD"
    main_password_not_entered = "MAIN_PASSWORD_NOT_ENTERED"
    sign_in = "SIGNED_IN_WITH_PASSWORD_SELECT_SCREEN"
    sign_in_selected = "SIGNED_IN_WITH_PASSWORD_SELECTED"
    sign_in_unselected = "SIGNED_IN_WITH_PASSWORD_NOT_SELECTED"


class PasswordManager:
    def __init__(self, window_name, window_size=None):
        self.show_warning = None
        self.raw_data = {}
        self.root = tk.Tk()
        self.sites = []
        self.selected = None
        self.password = None

        if window_size is not None:
            self.root.geometry(window_size)

        with open("configs.json") as configs:
            self.configs = json.loads(configs.read())

        self.state = States.main_password_not_entered

        self.root.title(window_name)

        # MAIN Widgets
        self.main_title = tk.Label(self.root)
        self.main_title.configure(text="Enter Password", font=self.configs["Fonts"]["Title"])
        self.main_title_settings = self.configs["Places"]["Title"]

        self.master_password_box = PlaceholderEntry(self.root, "Enter password...", special=True)
        self.master_password_box.configure(width=19, font=self.configs["Fonts"]["Password Box"])
        self.master_password_box_settings = self.configs["Places"]["Password Box"]

        self.submit_button = tk.Button(self.root)
        self.submit_button.configure(text="Submit",
                                     bg="green", activebackground="light green",
                                     width=12, font=self.configs["Fonts"]["Submit Button"],
                                     command=lambda: self.check_password(self.master_password_box.get()))
        self.submit_button_settings = self.configs["Places"]["Submit Button"]

        self.status = tk.Label(self.root)
        self.status.configure(text="Verifying... please wait...", font=self.configs["Fonts"]["Status Label"])
        self.status_settings = self.configs["Places"]["Status Label"]

        # SIGNEDIN Widgets
        self.show = False
        self.show_button_packed = False

        self.password_info_frame = tk.Frame(self.root)
        self.password_info_frame_setings = self.configs["Places"]["Password Info Frame"]

        self.url_field = PlaceholderEntry(self.password_info_frame, "URL")
        self.url_field.configure(width=24, font=self.configs["Fonts"]["Default"])
        self.url_field_setings = self.configs["Places"]["URL Field"]

        self.username_field = PlaceholderEntry(self.password_info_frame, "USERNAME")
        self.username_field.configure(width=12, font=self.configs["Fonts"]["Default"])
        self.username_field_setings = self.configs["Places"]["USERNAME Field"]

        self.password_field = PlaceholderEntry(self.password_info_frame, "PASSWORD", show="\u2022")
        self.password_field.configure(width=12, font=self.configs["Fonts"]["Default"])
        self.password_field_settings = self.configs["Places"]["PASSWORD Field"]

        self.add_button = tk.Button(self.root)
        self.add_button.configure(text="Add Entry", font=self.configs["Fonts"]["Default"], width=10,
                                  command=self.add_password, height=2)
        self.add_button_settings = self.configs["Places"]["Add Password"]

        self.remove_button = tk.Button(self.root)
        self.remove_button.configure(text="Delete Entry", font=self.configs["Fonts"]["Default"], width=13,
                                     command=self.remove_password, height=2)
        self.remove_button_settings = self.configs["Places"]["Remove Password"]

        self.site_info_frame = tk.Frame(self.root)
        self.site_info_frame.configure(borderwidth=5, relief="raised", width=50, height=8)
        self.site_info_frame_settings = self.configs["Places"]["Web Info Frame"]

        self.site_list_frame = tk.Frame(self.root)
        self.site_list_frame.configure(borderwidth=5, relief="raised", width=50, height=35)
        self.site_list_frame_settings = self.configs["Places"]["Web List Frame"]

        self.site_info = tk.Label(self.site_info_frame)
        self.site_info.configure(font=self.configs["Fonts"]["Web Info"],
                                 text="You have not selected a website yet.\nSelect one to view its properties.",
                                 width=50, height=7)
        self.site_info_settings = self.configs["Places"]["Site Info"]

        self.show_button = tk.Checkbutton(self.site_info_frame)
        self.show_button.configure(text="Show", command=self.show_password_toggle)
        self.show_button_settings = self.configs["Places"]["Show Button"]

        self.site_listbox = tk.Listbox(self.site_list_frame, height=13, width=40)
        self.web_scrollbar = tk.Scrollbar(self.site_list_frame, orient="vertical")

        self.site_listbox.configure(yscrollcommand=self.web_scrollbar.set)
        self.web_scrollbar.configure(command=self.site_listbox.yview)

        self.site_listbox_settings = self.configs["Places"]["Web Listbox"]
        self.web_scrollbar_settings = self.configs["Places"]["Web Scrollbar"]

        # self.web_name = tk.Label(self.root)
        # self.web_name_settings = self.configs["Places"]["Web Title"]
        # TODO add site title like example.com\nblah

        # Booleans
        self.running = True
        self.listbox_insert = True

    def password_show_check(self):
        self.selected = self.site_listbox.curselection()

        if not self.selected:
            return

        password = self.sites[self.selected[0]][EntryInfo.PASSWORD.value]

        self.site_info.config(
            text=f"Username: {self.sites[self.selected[0]][EntryInfo.USERNAME.value]}\nPassword: "
                 f"{password if self.show else "*" * len(password)}")

    def show_password_toggle(self):
        if not self.show_button_packed:
            self.show_button.pack(**self.show_button_settings)
            self.show_button_packed = True

        self.show = not self.show
        self.password_show_check()

    def add_password(self):
        self.sites.append([self.url_field.get(), self.password_field.get(), self.username_field.get()])

        if not all(self.sites[-1]):
            return False

        write_vault("passwords.json", str(self.sites))
        encrypt_vault("passwords.json", self.password.encode())

        self.site_listbox.delete(0, tk.END)
        self.listbox_insert = True
        self.state_display()

        return True

    def remove_password(self):
        confirm_false = None

        def toggle():
            nonlocal self

            self.show_warning = not self.show_warning

        def confirm():
            nonlocal confirm_false

            confirm_false = True

        def cancel():
            nonlocal confirm_false

            confirm_false = False

        # https://www.pythontutorial.net/tkinter/tkinter-toplevel/
        class WarningMessage(tk.Toplevel):
            def __init__(self, parent,
                         toggle_func,
                         yes_func=None,
                         no_func=None,
                         show=True):
                super().__init__(parent)

                if no_func is None:
                    no_func = self.destroy()

                if yes_func is None:
                    yes_func = self.destroy()

                self.geometry("110x150")
                self.title("Delete Entry")

                self.cancel = tk.Button(self, text="Cancel", command=no_func, width=9)
                self.confirm = tk.Button(self, text="Confirm", command=yes_func, width=9)
                self.dontshowagain_checkbox = tk.Checkbutton(self, text="Do not show again", command=toggle_func)

                self.cancel.grid(column=0, row=0)
                self.confirm.grid(column=1, row=0)

                if show:
                    self.dontshowagain_checkbox.pack(side="bottom")

        warning_msg = WarningMessage(self.root, toggle, confirm, cancel)

        if confirm_false:
            return False

        try:
            self.sites.pop(self.selected[0])

        except ValueError as error:
            print(error)

            return False

        write_vault("passwords.json", str(self.sites))
        encrypt_vault("passwords.json", self.password.encode())

        self.site_listbox.delete(self.selected[0], self.selected[0])
        self.listbox_insert = True
        self.state_display()

        return True

    def check_password(self, password):
        try:
            self.status.place(**self.status_settings)

            self.raw_data = decrypt_file("passwords.json", password)
            self.sites = self.raw_data["data"]
            self.show_warning = self.raw_data["show"]
            self.password = password

            self.main_title.configure(text="Password Manager")
            self.master_password_box.place_forget()
            self.status.place_forget()
            self.submit_button.place_forget()

            self.state = States.sign_in
            self.state_display()

        except:
            self.status.configure(text="ERROR: Incorrect Password")

            return False

    def state_display(self):
        def listbox_selected(event):
            self.state = States.sign_in_selected
            self.selected = self.site_listbox.curselection()

            self.state_display()

        if self.state == States.main:
            if self.master_password_box.get():
                self.state = States.main_password_entered

            else:
                self.state = States.main_password_not_entered

        if self.state == States.sign_in:
            if bool(self.site_listbox.curselection()):
                self.state = States.sign_in_selected

            else:
                self.state = States.sign_in_unselected

        match self.state:
            case States.main_password_not_entered:
                self.main_title.place(**self.main_title_settings)
                self.master_password_box.place(**self.master_password_box_settings)
                self.submit_button.place(**self.submit_button_settings)

            case States.main_password_not_entered:
                self.submit_button["state"] = "disabled"

            case States.main_password_entered:
                self.submit_button["state"] = "normal"

            case States.sign_in_unselected:
                self.site_info_frame.place(**self.site_info_frame_settings)
                self.site_info.pack(**self.site_info_settings)
                self.site_list_frame.place(**self.site_list_frame_settings)
                self.site_listbox.pack(**self.site_listbox_settings)
                self.root.bind("<<ListboxSelect>>", listbox_selected)
                self.submit_button.place_forget()
                self.master_password_box.place_forget()
                self.main_title.config(text="Password Manager")
                self.add_button.place(**self.add_button_settings)
                self.remove_button.place(**self.remove_button_settings)
                self.password_info_frame.place(**self.password_info_frame_setings)
                self.url_field.pack(**self.url_field_setings)
                self.username_field.pack(**self.username_field_setings)
                self.password_field.pack(**self.password_field_settings)

                if self.listbox_insert:
                    for s in range(len(self.sites)):
                        self.site_listbox.insert(s, self.sites[s][EntryInfo.URL.value])

                    self.listbox_insert = False

            case States.sign_in_unselected:
                self.show_button.pack_forget()
                self.show_button_packed = False
                self.password_show_check()

            case States.sign_in_selected:
                self.show_button.pack(**self.show_button_settings)
                self.show_button_packed = True
                self.password_show_check()

    def main(self):
        self.state_display()

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        self.root.geometry(f"{int(sw // 1.2 if sw > 1250 else sw)}x{int(sh // 1.25 if sh > 850 else sh)}")
        self.root.mainloop()


# https://stackoverflow.com/questions/27820178/how-to-add-placeholder-to-an-entry-in-tkinter
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color="grey", show=None, special=False):
        super().__init__(master, show=show)

        self.special = special

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self["fg"]
        self.show = show

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self["fg"] = self.placeholder_color

    def foc_in(self, *args):
        if self["fg"] == self.placeholder_color:
            self["show"] = self.show
            self.delete("0", "end")
            self["fg"] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self["show"] = None
            self.put_placeholder()


if __name__ == "__main__":
    pm = PasswordManager("Password Manager")
    pm.main()

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
    def __init__(self, window_name, window_size=None, **kwargs):
        self.root = tk.Tk()
        self.sites = []

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

        self.master_password_box = tk.Entry(self.root)
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
        self.status_settings = self.configs["Places"]["Verifying/Error Label"]

        # SIGNEDIN Widgets
        self.show = False
        self.show_button_packed = False

        self.add_button = tk.Button(self.root)
        self.add_button.configure(text="Add Password", font=self.configs["Fonts"]["Places"], width=16,
                                  command=self.add_password)
        # TODO: complete the ADD_PASSWORD and "DELETE/REMOVE"_PASSWORD by next Tuesday

        self.site_info_frame = tk.Frame(self.root)
        self.site_info_frame.configure(borderwidth=5, relief="raised", width=50, height=8)
        self.site_info_frame_settings = self.configs["Places"]["Web Info Frame"]

        self.site_list_frame = tk.Frame(self.root)
        self.site_list_frame.configure(borderwidth=5, relief="raised", width=50, height=35)
        self.site_list_frame_settings = self.configs["Places"]["Web List Frame"]

        self.site_info = tk.Label(self.site_info_frame)
        self.site_info.configure(font=self.configs["Fonts"]["Web Info"],
                                 text="You have not selected anything yet.\nSelect one to view its properties.",
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

        # self.web_name = tk.Label()
        # self.web_name_settings = self.configs["Places"]["Web Title"]
        # TODO add site title like example.com\nblah

        # Booleans
        self.running = True
        self.listbox_insert = True

    def password_show_check(self):
        selected = self.site_listbox.curselection()
        password = self.sites[selected[0]][EntryInfo.PASSWORD.value]

        self.site_info.config(
            text=f"Username: {self.sites[selected[0]][EntryInfo.USERNAME.value]}\nPassword: "
                 f"{password if self.show else "*" * len(password)}")

    def show_password_toggle(self):
        if not self.show_button_packed:
            self.show_button.pack(**self.show_button_settings)
            self.show_button_packed = True

        self.show = not self.show
        self.password_show_check()

    def add_password(self, password):
        ...

    def check_password(self, password):
        try:
            self.status.place(**self.status_settings)
            self.sites = decrypt_file("passwords.json", password)
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
    def __init__(self, master=None, placeholder="PLACEHOLDER", color="grey"):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self["fg"]

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self["fg"] = self.placeholder_color

    def foc_in(self, *args):
        if self["fg"] == self.placeholder_color:
            self["show"] = "\u2022"
            self.delete("0", "end")
            self["fg"] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self["show"] = None
            self.put_placeholder()


if __name__ == "__main__":
    pm = PasswordManager("Password Manager")
    pm.main()

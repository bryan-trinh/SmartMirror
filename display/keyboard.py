# keyboard.py
# References:
# https://masterprograming.com/how-to-create-virtual-onscreen-keyboard-using-python-and-tkinter/
# https://www.bitforestinfo.com/2017/03/how-to-create-virtual-keyboard-using.html

from tkinter import *

# add in CapsLock & Shift (symbols?)
KEYS = [
    ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"),
    ("q", "w", "e", "r", "t", "y", "u", "i", "o", "p"),
    ("Caps\nLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", "Enter"),
    ("Shift", "z", "x", "c", "v", "b", "n", "m", ","),
    ("", "Space", "")
]

class Keyboard(Frame):
    def __init__(self, master=None):
        super().__init__(master, background="black", bd=5)
        self.master = master
        self.pack(side=TOP, expand=YES, fill=BOTH)

        self.caps_on  = False  # whether CapsLock is on
        self.shift_on = True   # whether Shift is on
        self.cap_keys = False  # whether button text is capitalized

        self.prompt = ""
        self.result = ""
        self.is_open = BooleanVar(self.master, True)
        self.buttons = []

        self.create_keyboard()
        self.update_case()

    def create_keyboard(self):
        row_frame = Frame(self, background="black")
        row_frame.pack(side=TOP, expand=YES, fill=BOTH)
        self.text = Label(row_frame, text=self.prompt+self.result, bg="black", fg="white")
        self.text.config(font=("Bahnschrift", 15))
        self.text.pack(expand=YES, fill=BOTH, padx=5, pady=5)

        for row in KEYS:
            row_frame = Frame(self, background="black")
            row_frame.pack(side=TOP, expand=YES, fill=BOTH)

            for k in row:
                k_button = Button(row_frame, text=k, bg="grey10", fg="white", relief=FLAT)
                self.buttons.append(k_button)

                if k == "":
                    k_button.config(state=DISABLED, bg="black", relief=FLAT)

                k_button.config(font=("Bahnschrift", 15))
                k_button['command'] = lambda q=k: self.button_command(q)
                k_button.pack(side=LEFT, expand=YES, fill=BOTH, padx=5, pady=5)

    def button_command(self, key):
        if key == "Backspace":
            self.result = self.result[:-1]
            
        elif key == "Enter":
            self.is_open.set(False)
            self.master.withdraw()

        elif key == "Caps\nLock":
            self.caps_on = not self.caps_on
            self.update_case()

        elif key == "Shift":
            self.shift_on = not self.shift_on
            self.update_case()

        elif key == "Space":
            self.result += " "

        elif key == "":
            pass

        else:
            if self.caps_on or self.shift_on:
                 self.result += key.capitalize()

            else:
                self.result += key

            self.shift_on = False
            self.update_case()

        self.text["text"] = self.prompt + self.result

    def update_case(self):
        # if CapsLock and Shift are not on but the keys are capitalized,
        # make the keys lowercase
        if not self.caps_on and not self.shift_on and self.cap_keys:
            for b in self.buttons:
                if len(b["text"]) == 1:
                    b["text"] = b["text"].lower()

            self.cap_keys = False

        # if CapsLock or Shift are on and the keys are NOT capitalized,
        # make the keys uppercase
        elif (self.caps_on or self.shift_on) and not self.cap_keys:
            for b in self.buttons:
                if len(b["text"]) == 1:
                    b["text"] = b["text"].upper()

            self.cap_keys = True

    def refresh(self):
        self.shift_on = True
        self.update_case()

        self.is_open.set(True)
        self.result = ""
        self.text["text"] = self.prompt + self.result

        self.master.deiconify()

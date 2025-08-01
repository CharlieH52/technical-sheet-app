from tkinter import messagebox, Tk

class PopUp:
    def __init__(self, window_title:str, content_message: str):
        tk = Tk()
        tk.withdraw()
        messagebox.showinfo(window_title, content_message)
        tk.destroy()
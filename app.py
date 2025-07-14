import customtkinter as ctk
from view import MainView

class VersionaryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Versionary - Version Control System")
        self.geometry("1000x600")
        self.minsize(800, 500)

        self.main_view = MainView(self)
        self.main_view.pack(expand=True, fill="both")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = VersionaryApp()
    app.mainloop()

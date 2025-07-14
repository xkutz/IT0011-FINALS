import customtkinter as ctk

class MainView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Layout: Sidebar + Main Area
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = ctk.CTkFrame(self)
        self.main_area.pack(side="right", expand=True, fill="both")

        # Sidebar Navigation Buttons
        ctk.CTkLabel(self.sidebar, text="📁 Navigation", font=("Arial", 18)).pack(pady=(20, 10))

        self.dashboard_button = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.load_view(DashboardView))
        self.dashboard_button.pack(pady=5, padx=10, fill="x")

        self.software_button = ctk.CTkButton(self.sidebar, text="Software Versions", command=lambda: self.load_view(SoftwareVersionView))
        self.software_button.pack(pady=5, padx=10, fill="x")

        # Initial view
        self.current_view = None
        self.load_view(DashboardView)

    def load_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.main_area)
        self.current_view.pack(expand=True, fill="both")


# ---- Views ----

class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="📊 Dashboard", font=("Arial", 22)).pack(pady=20)

        ctk.CTkLabel(self, text="Recent activity will be shown here...", font=("Arial", 14)).pack(pady=10)


class SoftwareVersionView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.controller = master.master  # Reference to app.py

        ctk.CTkLabel(self, text="🛠 Software Versions", font=("Arial", 22)).pack(pady=20)

        form = ctk.CTkFrame(self)
        form.pack(pady=10, padx=20, fill="x")

        # Software Name
        ctk.CTkLabel(form, text="Software Name").pack(anchor="w")
        self.software_name_entry = ctk.CTkEntry(form, placeholder_text="e.g. BugTracker, GameApp")
        self.software_name_entry.pack(fill="x", pady=5)

        # Version Number
        ctk.CTkLabel(form, text="Version Number").pack(anchor="w")
        self.version_number_entry = ctk.CTkEntry(form, placeholder_text="e.g. 1.0.0")
        self.version_number_entry.pack(fill="x", pady=5)

        # Release Date
        ctk.CTkLabel(form, text="Release Date").pack(anchor="w")
        self.release_date_entry = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD")
        self.release_date_entry.pack(fill="x", pady=5)

        # Status
        ctk.CTkLabel(form, text="Status").pack(anchor="w")
        self.status_option = ctk.CTkOptionMenu(form, values=["Stable", "Beta", "Deprecated"])
        self.status_option.set("Stable")
        self.status_option.pack(fill="x", pady=5)

        # Notes
        ctk.CTkLabel(form, text="Notes").pack(anchor="w")
        self.notes_entry = ctk.CTkTextbox(form, height=80)
        self.notes_entry.pack(fill="x", pady=5)

        # Button
        ctk.CTkButton(form, text="Add Version", command=self.add_version).pack(pady=10)

        # Version list
        self.version_list_frame = ctk.CTkScrollableFrame(self, label_text="All Software Versions")
        self.version_list_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh_version_list()

    def add_version(self):
        software_name = self.software_name_entry.get().strip()
        version_number = self.version_number_entry.get().strip()
        release_date = self.release_date_entry.get().strip()
        status = self.status_option.get()
        notes = self.notes_entry.get("1.0", "end").strip()

        if not software_name or not version_number:
            return  # You can add a popup alert here if needed

        self.controller.add_version(software_name, version_number, release_date, status, notes)
        self.clear_form()
        self.refresh_version_list()

    def clear_form(self):
        self.software_name_entry.delete(0, "end")
        self.version_number_entry.delete(0, "end")
        self.release_date_entry.delete(0, "end")
        self.status_option.set("Stable")
        self.notes_entry.delete("1.0", "end")

    def refresh_version_list(self):
        for widget in self.version_list_frame.winfo_children():
            widget.destroy()

        versions = self.controller.get_versions()
        for version in versions:
            version_id, software_name, version_number, date, status, notes = version
            text = f"📦 {software_name} | {version_number} | {status} | {date}"
            ctk.CTkLabel(self.version_list_frame, text=text, anchor="w").pack(anchor="w", pady=2, padx=5)


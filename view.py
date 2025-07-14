# view.py
import customtkinter as ctk
from db import VersionController

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="📊 Dashboard", font=("Arial", 20)).pack(pady=10)

        self.software_entry = ctk.CTkEntry(self, placeholder_text="Enter new software name")
        self.software_entry.pack(pady=5, fill="x", padx=10)

        self.add_button = ctk.CTkButton(self, text="Add Software", command=self.add_software)
        self.add_button.pack(pady=5)

        self.software_dropdown = ctk.CTkOptionMenu(self, values=["Loading..."], command=self.change_selected_software)
        self.software_dropdown.pack(pady=10, fill="x", padx=10)

        self.load_softwares()

    def add_software(self):
        name = self.software_entry.get().strip()
        if name:
            self.controller.add_software(name)
            self.software_entry.delete(0, ctk.END)
            self.load_softwares()

    def load_softwares(self):
        softwares = self.controller.get_softwares()
        self.software_map = {name: sid for sid, name in softwares}
        self.software_dropdown.configure(values=list(self.software_map.keys()))
        if softwares:
            first = softwares[0][1]
            self.software_dropdown.set(first)
            self.controller.set_active_software(self.software_map[first])

    def change_selected_software(self, selected_name):
        software_id = self.software_map.get(selected_name)
        if software_id:
            self.controller.set_active_software(software_id)

class VersionDetailsView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_version_id = None

        ctk.CTkLabel(self, text="📜 Version Details", font=("Arial", 20)).pack(pady=10)

        self.version_number_entry = ctk.CTkEntry(self, placeholder_text="Version Number (e.g., 1.0.0)")
        self.version_number_entry.pack(pady=2, padx=10, fill="x")

        self.release_date_entry = ctk.CTkEntry(self, placeholder_text="Release Date (YYYY-MM-DD)")
        self.release_date_entry.pack(pady=2, padx=10, fill="x")

        self.status_entry = ctk.CTkOptionMenu(self, values=["Stable", "Beta", "Deprecated"])
        self.status_entry.set("Stable")
        self.status_entry.pack(pady=2, padx=10, fill="x")

        self.notes_entry = ctk.CTkEntry(self, placeholder_text="Notes")
        self.notes_entry.pack(pady=2, padx=10, fill="x")

        self.add_version_button = ctk.CTkButton(self, text="Add Version", command=self.add_or_update_version)
        self.add_version_button.pack(pady=5, padx=10, fill="x")

        self.delete_button = ctk.CTkButton(self, text="Delete Version", command=self.delete_version, fg_color="red")
        self.delete_button.pack(pady=2, padx=10, fill="x")

        self.version_list_frame = ctk.CTkScrollableFrame(self)
        self.version_list_frame.pack(pady=10, fill="both", expand=True)

        # Header row
        ctk.CTkLabel(self.version_list_frame, text="Version", anchor="w", width=100).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(self.version_list_frame, text="Release Date", anchor="w", width=120).grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(self.version_list_frame, text="Status", anchor="w", width=100).grid(row=0, column=2, sticky="w", padx=5)
        ctk.CTkLabel(self.version_list_frame, text="Notes", anchor="w", width=200).grid(row=0, column=3, sticky="w", padx=5)

        self.refresh_version_list()

    def refresh_version_list(self):
        for widget in self.version_list_frame.winfo_children()[4:]:  # Skip the headers
            widget.destroy()

        software_id = self.controller.get_active_software()
        if software_id:
            versions = self.controller.get_versions(software_id)
            for i, (version_id, version_number, release_date, status, notes) in enumerate(versions, start=1):
                ctk.CTkButton(
                    self.version_list_frame,
                    text=version_number,
                    command=lambda v=(version_id, version_number, release_date, status, notes): self.load_version_for_edit(v),
                    anchor="w"
                ).grid(row=i, column=0, sticky="w", padx=5)

                ctk.CTkLabel(self.version_list_frame, text=release_date, anchor="w").grid(row=i, column=1, sticky="w", padx=5)
                ctk.CTkLabel(self.version_list_frame, text=status, anchor="w").grid(row=i, column=2, sticky="w", padx=5)
                ctk.CTkLabel(self.version_list_frame, text=notes, anchor="w").grid(row=i, column=3, sticky="w", padx=5)

    def load_version_for_edit(self, version):
        self.selected_version_id, number, date, status, notes = version
        self.version_number_entry.delete(0, ctk.END)
        self.version_number_entry.insert(0, number)
        self.release_date_entry.delete(0, ctk.END)
        self.release_date_entry.insert(0, date)
        self.status_entry.set(status)
        self.notes_entry.delete(0, ctk.END)
        self.notes_entry.insert(0, notes)
        self.add_version_button.configure(text="Update Version")

    def add_or_update_version(self):
        version = self.version_number_entry.get()
        date = self.release_date_entry.get()
        status = self.status_entry.get()
        notes = self.notes_entry.get()
        software_id = self.controller.get_active_software()

        if not version or not software_id:
            return

        if self.selected_version_id:
            self.controller.update_version(self.selected_version_id, version, date, status, notes)
        else:
            self.controller.add_version(software_id, version, date, status, notes)

        self.clear_form()
        self.refresh_version_list()

    def delete_version(self):
        if self.selected_version_id:
            self.controller.delete_version(self.selected_version_id)
            self.clear_form()
            self.refresh_version_list()

    def clear_form(self):
        self.selected_version_id = None
        self.version_number_entry.delete(0, ctk.END)
        self.release_date_entry.delete(0, ctk.END)
        self.status_entry.set("Stable")
        self.notes_entry.delete(0, ctk.END)
        self.add_version_button.configure(text="Add Version")

class BugTrackingView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        ctk.CTkLabel(self, text="🔎 Bug Tracking").pack(pady=20)

class ReleaseManagementView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        ctk.CTkLabel(self, text="🚀 Release Management").pack(pady=20)

class VersionTimelineView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        ctk.CTkLabel(self, text="🕒 Version History Timeline").pack(pady=20)

class MainView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.controller = VersionController()

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = ctk.CTkFrame(self)
        self.main_area.pack(side="right", expand=True, fill="both")

        self.views = {
            "Dashboard": DashboardView,
            "Version Details": VersionDetailsView,
            "Bug Tracking": BugTrackingView,
            "Release Management": ReleaseManagementView,
            "Version Timeline": VersionTimelineView
        }

        for name, view_class in self.views.items():
            btn = ctk.CTkButton(self.sidebar, text=name, command=lambda v=view_class: self.load_view(v))
            btn.pack(pady=5, padx=10, fill="x")

        self.current_view = None
        self.load_view(DashboardView)

    def load_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.main_area, self.controller)
        self.current_view.pack(expand=True, fill="both")




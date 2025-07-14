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
        self.controller = controller
        self.selected_bug_id = None

        ctk.CTkLabel(self, text="🐞 Bug Tracking", font=("Arial", 20)).pack(pady=10)

        # --- Bug Entry Form ---
        self.version_dropdown = ctk.CTkOptionMenu(self, values=["Loading..."])
        self.version_dropdown.pack(pady=2, padx=10, fill="x")

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Bug Title")
        self.title_entry.pack(pady=2, padx=10, fill="x")

        self.description_entry = ctk.CTkEntry(self, placeholder_text="Description")
        self.description_entry.pack(pady=2, padx=10, fill="x")

        self.severity_menu = ctk.CTkOptionMenu(self, values=["Critical", "Major", "Minor"])
        self.severity_menu.set("Major")
        self.severity_menu.pack(pady=2, padx=10, fill="x")

        self.status_menu = ctk.CTkOptionMenu(self, values=["Open", "Resolved", "Closed"])
        self.status_menu.set("Open")
        self.status_menu.pack(pady=2, padx=10, fill="x")

        self.assigned_to_entry = ctk.CTkEntry(self, placeholder_text="Assigned To")
        self.assigned_to_entry.pack(pady=2, padx=10, fill="x")

        self.date_reported_entry = ctk.CTkEntry(self, placeholder_text="Date Reported (YYYY-MM-DD)")
        self.date_reported_entry.pack(pady=2, padx=10, fill="x")

        self.add_bug_button = ctk.CTkButton(self, text="Add Bug", command=self.add_or_update_bug)
        self.add_bug_button.pack(pady=5, padx=10, fill="x")

        self.delete_bug_button = ctk.CTkButton(self, text="Delete Bug", command=self.delete_bug, fg_color="red")
        self.delete_bug_button.pack(pady=2, padx=10, fill="x")

        # --- Bug List ---
        self.bug_list_frame = ctk.CTkScrollableFrame(self)
        self.bug_list_frame.pack(pady=10, fill="both", expand=True)

        self.refresh_bug_versions()
        self.refresh_bug_list()

    def refresh_bug_versions(self):
        software_id = self.controller.get_active_software()
        if not software_id:
            return

        versions = self.controller.get_versions(software_id)
        self.version_map = {f"{v[1]} ({v[2]})": v[0] for v in versions}
        self.version_dropdown.configure(values=list(self.version_map.keys()))
        if versions:
            self.version_dropdown.set(list(self.version_map.keys())[0])

    def refresh_bug_list(self):
        for widget in self.bug_list_frame.winfo_children():
            widget.destroy()

        software_id = self.controller.get_active_software()
        if not software_id:
            return

        bugs = self.controller.get_bugs_by_software(software_id)

        for bug in bugs:
            bug_id, title, description, severity, status, assigned_to, date_reported, version_number = bug
            text = f"[{version_number}] {title} | {severity} | {status}\nAssigned to: {assigned_to} | Reported: {date_reported}\n{description}"
            btn = ctk.CTkButton(
                self.bug_list_frame,
                text=text,
                command=lambda b=bug: self.load_bug_for_edit(b),
                anchor="w"
            )
            btn.pack(fill="x", padx=5, pady=2)

    def load_bug_for_edit(self, bug):
        self.selected_bug_id, title, description, severity, status, assigned_to, date_reported, version_number = bug
        self.version_dropdown.set(f"{version_number}")
        self.title_entry.delete(0, ctk.END)
        self.title_entry.insert(0, title)
        self.description_entry.delete(0, ctk.END)
        self.description_entry.insert(0, description)
        self.severity_menu.set(severity)
        self.status_menu.set(status)
        self.assigned_to_entry.delete(0, ctk.END)
        self.assigned_to_entry.insert(0, assigned_to)
        self.date_reported_entry.delete(0, ctk.END)
        self.date_reported_entry.insert(0, date_reported)
        self.add_bug_button.configure(text="Update Bug")

    def clear_form(self):
        self.selected_bug_id = None
        self.title_entry.delete(0, ctk.END)
        self.description_entry.delete(0, ctk.END)
        self.assigned_to_entry.delete(0, ctk.END)
        self.date_reported_entry.delete(0, ctk.END)
        self.severity_menu.set("Major")
        self.status_menu.set("Open")
        self.add_bug_button.configure(text="Add Bug")


    def add_or_update_bug(self):
        version_key = self.version_dropdown.get()
        version_id = self.version_map.get(version_key)
        if not version_id:
            return

        title = self.title_entry.get()
        description = self.description_entry.get()
        severity = self.severity_menu.get()
        status = self.status_menu.get()
        assigned_to = self.assigned_to_entry.get()
        date_reported = self.date_reported_entry.get()

        if not title or not date_reported:
            return

        if self.selected_bug_id:
            self.controller.update_bug(self.selected_bug_id, title, description, severity, status, assigned_to, date_reported)
        else:
            self.controller.add_bug(version_id, title, description, severity, status, assigned_to, date_reported)

        self.clear_form()
        self.refresh_bug_list()


    def delete_bug(self):
        if self.selected_bug_id:
            self.controller.delete_bug(self.selected_bug_id)
            self.clear_form()
            self.refresh_bug_list()

class ReleaseManagementView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_deployment_id = None

        ctk.CTkLabel(self, text="🚀 Release Management", font=("Arial", 20)).pack(pady=10)

        self.environment_entry = ctk.CTkOptionMenu(self, values=["Production", "Staging", "Testing"])
        self.environment_entry.set("Production")
        self.environment_entry.pack(pady=2, padx=10, fill="x")

        self.deployment_date_entry = ctk.CTkEntry(self, placeholder_text="Deployment Date (YYYY-MM-DD)")
        self.deployment_date_entry.pack(pady=2, padx=10, fill="x")

        self.status_entry = ctk.CTkOptionMenu(self, values=["Pending", "Successful", "Failed"])
        self.status_entry.set("Pending")
        self.status_entry.pack(pady=2, padx=10, fill="x")

        self.add_deployment_button = ctk.CTkButton(self, text="Add Deployment", command=self.add_or_update_deployment)
        self.add_deployment_button.pack(pady=5, padx=10, fill="x")

        self.delete_button = ctk.CTkButton(self, text="Delete Deployment", command=self.delete_deployment, fg_color="red")
        self.delete_button.pack(pady=2, padx=10, fill="x")

        self.deployment_list_frame = ctk.CTkScrollableFrame(self)
        self.deployment_list_frame.pack(pady=10, fill="both", expand=True)

        # Header row
        ctk.CTkLabel(self.deployment_list_frame, text="Environment", anchor="w", width=120).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(self.deployment_list_frame, text="Date", anchor="w", width=120).grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(self.deployment_list_frame, text="Status", anchor="w", width=100).grid(row=0, column=2, sticky="w", padx=5)

        self.refresh_deployment_list()

    def refresh_deployment_list(self):
        for widget in self.deployment_list_frame.winfo_children()[3:]:
            widget.destroy()

        software_id = self.controller.get_active_software()
        if software_id:
            deployments = self.controller.get_deployments(software_id)
            for i, (deployment_id, env, date, status) in enumerate(deployments, start=1):
                ctk.CTkButton(
                    self.deployment_list_frame,
                    text=env,
                    command=lambda d=(deployment_id, env, date, status): self.load_deployment_for_edit(d),
                    anchor="w"
                ).grid(row=i, column=0, sticky="w", padx=5)

                ctk.CTkLabel(self.deployment_list_frame, text=date, anchor="w").grid(row=i, column=1, sticky="w", padx=5)
                ctk.CTkLabel(self.deployment_list_frame, text=status, anchor="w").grid(row=i, column=2, sticky="w", padx=5)

    def load_deployment_for_edit(self, deployment):
        self.selected_deployment_id, env, date, status = deployment
        self.environment_entry.set(env)
        self.deployment_date_entry.delete(0, ctk.END)
        self.deployment_date_entry.insert(0, date)
        self.status_entry.set(status)
        self.add_deployment_button.configure(text="Update Deployment")

    def add_or_update_deployment(self):
        env = self.environment_entry.get()
        date = self.deployment_date_entry.get()
        status = self.status_entry.get()
        software_id = self.controller.get_active_software()

        if not env or not date or not software_id:
            return

        if self.selected_deployment_id:
            self.controller.update_deployment(self.selected_deployment_id, env, date, status)
        else:
            self.controller.add_deployment(software_id, env, date, status)

        self.clear_form()
        self.refresh_deployment_list()

    def delete_deployment(self):
        if self.selected_deployment_id:
            self.controller.delete_deployment(self.selected_deployment_id)
            self.clear_form()
            self.refresh_deployment_list()

    def clear_form(self):
        self.selected_deployment_id = None
        self.environment_entry.set("Production")
        self.deployment_date_entry.delete(0, ctk.END)
        self.status_entry.set("Pending")
        self.add_deployment_button.configure(text="Add Deployment")


class VersionTimelineView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="🕒 Version History Timeline", font=("Arial", 20)).pack(pady=10)

        self.timeline_frame = ctk.CTkScrollableFrame(self)
        self.timeline_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.refresh_timeline()

    def refresh_timeline(self):
        for widget in self.timeline_frame.winfo_children():
            widget.destroy()

        software_id = self.controller.get_active_software()
        if software_id:
            versions = self.controller.get_versions(software_id)
            for version_id, number, date, status, notes in versions:
                color = {
                    "Stable": "🟢",
                    "Beta": "🟡",
                    "Deprecated": "🔴"
                }.get(status, "⬜")

                display = f"{color} {number} ({date})\nStatus: {status}\nNotes: {notes}\n"
                label = ctk.CTkLabel(self.timeline_frame, text=display, anchor="w", justify="left")
                label.pack(anchor="w", pady=4, fill="x")




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




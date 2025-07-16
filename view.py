import customtkinter as ctk
from db import VersionController
import os
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import messagebox


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

        self.summary_label = ctk.CTkLabel(self, text="Loading recent activity...", justify="left", anchor="w")
        self.summary_label.pack(pady=10, padx=10, fill="x")
        
        self.software_list_frame = ctk.CTkScrollableFrame(self)
        self.software_list_frame.pack(pady=5, fill="both", expand=True, padx=10)

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

        #Refresh software display
        for widget in self.software_list_frame.winfo_children():
            widget.destroy()

        for sid, name in softwares:
            row = ctk.CTkFrame(self.software_list_frame)
            row.pack(fill="x", pady=2)

            label = ctk.CTkLabel(row, text=name, anchor="w")
            label.pack(side="left", fill="x", expand=True)

            edit_btn = ctk.CTkButton(row, text="✏️ rename", width=30, command=lambda sid=sid, n=name: self.edit_software_prompt(sid, n))
            edit_btn.pack(side="right", padx=2)

            del_btn = ctk.CTkButton(row, text="🗑️ delete", width=30, fg_color="red", command=lambda sid=sid: self.delete_software(sid))
            del_btn.pack(side="right", padx=2)
            self.update_summary()

    def edit_software_prompt(self, software_id, current_name):
        new_name = ctk.CTkInputDialog(text=f"Rename software '{current_name}' to:", title="Edit Software").get_input()
        if new_name and new_name.strip():
            self.controller.update_software(software_id, new_name.strip())
            self.load_softwares()

    def update_summary(self):
        software_id = self.controller.get_active_software()
        if not software_id:
            self.summary_label.configure(text="No software selected.")
            return

        #Get latest
        versions = self.controller.get_versions(software_id)
        latest_version = versions[0] if versions else None
        version_text = f"Latest Version: v{latest_version[1]} ({latest_version[3]})" if latest_version else "No versions yet."

        #Get latest patch
        patches = self.controller.get_patch_notes_by_software(software_id)
        latest_patch = patches[0] if patches else None
        patch_text = f"Latest Patch: {latest_patch[1]}" if latest_patch else "No patch notes yet."

        #Get latest bug
        bugs = self.controller.get_bugs_by_software(software_id)
        latest_bug = bugs[0] if bugs else None
        bug_text = f"Latest Bug: {latest_bug[1]}" if latest_bug else "No bugs reported."

        #Get latest deployment
        deployments = self.controller.get_deployments(software_id)
        latest_deployment = deployments[0] if deployments else None
        deploy_text = f"Last Deployment: {latest_deployment[1]} - {latest_deployment[2]} ({latest_deployment[3]})" if latest_deployment else "No deployments yet."

        summary = f"{version_text}\n{patch_text}\n{bug_text}\n{deploy_text}"
        self.summary_label.configure(text=summary)


    def delete_software(self, software_id):
        if messagebox.askyesno("Delete Software", "Are you sure you want to delete this software and all its data?"):
            self.controller.delete_software(software_id)
            self.load_softwares()
        


    def change_selected_software(self, selected_name):
        software_id = self.software_map.get(selected_name)
        if software_id:
            self.controller.set_active_software(software_id)
            self.update_summary()

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

        #Header row
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

        #Bug Entry Form
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

        #Bug List
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

class PatchNotesView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_image_path = None

        ctk.CTkLabel(self, text="📘 Patch Notes", font=("Arial", 20)).pack(pady=10)

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Note Title")
        self.title_entry.pack(pady=2, padx=10, fill="x")

        self.desc_entry = ctk.CTkEntry(self, placeholder_text="Note Description")
        self.desc_entry.pack(pady=2, padx=10, fill="x")

        self.image_button = ctk.CTkButton(self, text="Attach Image (Optional)", command=self.browse_image)
        self.image_button.pack(pady=2, padx=10, fill="x")

        self.preview_label = ctk.CTkLabel(self, text="", anchor="w")
        self.preview_label.pack(pady=2, padx=10, fill="x")

        self.add_button = ctk.CTkButton(self, text="Add Patch Note", command=self.add_patch_note)
        self.add_button.pack(pady=5, padx=10, fill="x")

        self.notes_frame = ctk.CTkScrollableFrame(self)
        self.notes_frame.pack(pady=10, fill="both", expand=True)

        self.refresh_notes()

    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if path:
            self.selected_image_path = path
            self.preview_label.configure(text=os.path.basename(path))

    def add_patch_note(self):
        version_id = self.controller.get_latest_version_id_for_active_software()
        title = self.title_entry.get()
        desc = self.desc_entry.get()
        image_path = self.selected_image_path

        if version_id and title:
            self.controller.add_patch_note(version_id, title, desc, image_path)
            self.clear_form()
            self.refresh_notes()

    def clear_form(self):
        self.title_entry.delete(0, ctk.END)
        self.desc_entry.delete(0, ctk.END)
        self.selected_image_path = None
        self.preview_label.configure(text="")

    def refresh_notes(self):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        software_id = self.controller.get_active_software()
        if software_id:
            notes = self.controller.get_patch_notes_by_software(software_id)
            for patch_id, title, desc, img_path, version_number in notes:
                frame = ctk.CTkFrame(self.notes_frame)
                frame.pack(fill="x", padx=10, pady=5)

                text = f"📌 {title} (v{version_number})\n{desc}"
                ctk.CTkLabel(frame, text=text, anchor="w", justify="left").pack(side="left", fill="both", expand=True)

                if img_path and os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((64, 64))
                        tk_img = ImageTk.PhotoImage(img)

                        def open_image(path=img_path):
                            if not os.path.exists(path):
                                return

                            top = ctk.CTkToplevel(self)
                            top.title(os.path.basename(path))
                            top.geometry("800x600")
                            
                            #Center window
                            top.update_idletasks()
                            w = 800
                            h = 600
                            x = (top.winfo_screenwidth() // 2) - (w // 2)
                            y = (top.winfo_screenheight() // 2) - (h // 2)
                            top.geometry(f"{w}x{h}+{x}+{y}")

                            canvas = ctk.CTkCanvas(top, bg="black", highlightthickness=0)
                            canvas.pack(fill="both", expand=True)

                            try:
                                original_img = Image.open(path)
                            except Exception as e:
                                ctk.CTkLabel(top, text=f"Error loading image: {e}").pack(pady=10)
                                return
                            
                            zoom_level = [0.5]

                            def render_image():
                                img = original_img.copy()
                                scale = zoom_level[0]
                                img = img.resize((int(original_img.width * scale), int(original_img.height * scale)))
                                tk_img = ImageTk.PhotoImage(img)
                                canvas.img = tk_img  # prevent GC
                                canvas.delete("all")
                                canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, anchor="center", image=tk_img)

                        #scrol
                            def zoom(event):
                                if event.delta > 0:
                                    zoom_level[0] *= 1.1
                                else:
                                    zoom_level[0] /= 1.1
                                render_image()

                            def save_image():
                                save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[
                                    ("PNG", "*.png"),
                                    ("JPEG", "*.jpg;*.jpeg"),
                                    ("GIF", "*.gif"),
                                    ("BMP", "*.bmp"),
                                    ("All files", "*.*")
                                ])
                                if save_path:
                                    original_img.save(save_path)

                            def close_popup():
                                top.destroy()

                            #Bind zoom
                            canvas.bind("<Configure>", lambda e: render_image())
                            canvas.bind("<MouseWheel>", zoom)
                            canvas.bind("<Button-4>", lambda e: zoom(type("Event", (), {"delta": 120})))
                            canvas.bind("<Button-5>", lambda e: zoom(type("Event", (), {"delta": -120})))

                            #Button Row
                            button_frame = ctk.CTkFrame(top)
                            button_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

                            close_btn = ctk.CTkButton(button_frame, text="❌", width=10, command=close_popup, fg_color="red", hover_color="#aa0000")
                            close_btn.pack(side="right", padx=5)

                            save_btn = ctk.CTkButton(button_frame, text="💾 Save As...", command=save_image)
                            save_btn.pack(side="right", padx=5)

                            render_image()


                        img_label = ctk.CTkLabel(frame, image=tk_img, text="")
                        img_label.image = tk_img
                        img_label.pack(side="right", padx=5)
                        img_label.bind("<Button-1>", lambda e, p=img_path: open_image(p))
                    except:
                        pass

                del_btn = ctk.CTkButton(frame, text="❌", width=10, command=lambda pid=patch_id: self.delete_patch_note(pid))
                del_btn.pack(side="right", padx=5)


    def delete_patch_note(self, patch_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patch note?"):
            self.controller.delete_patch_note(patch_id)
            self.refresh_notes()


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
            "Version Timeline": VersionTimelineView,
            "Patch Notes": PatchNotesView,
            
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
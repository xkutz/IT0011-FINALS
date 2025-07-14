import sqlite3

class VersionController:
    def __init__(self, db_path="versionary.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.active_software_id = None
        self.create_tables()

    def create_tables(self):
        self.cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Softwares (
            software_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Software_Versions (
            version_id INTEGER PRIMARY KEY AUTOINCREMENT,
            software_id INTEGER,
            version_number TEXT NOT NULL,
            release_date TEXT,
            status TEXT,
            notes TEXT,
            FOREIGN KEY (software_id) REFERENCES Softwares(software_id)
        );

        CREATE TABLE IF NOT EXISTS Updates (
            update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER,
            update_type TEXT,
            update_description TEXT,
            date_applied TEXT,
            FOREIGN KEY (version_id) REFERENCES Software_Versions(version_id)
        );

        CREATE TABLE IF NOT EXISTS Bugs (
            bug_id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER,
            title TEXT,
            description TEXT,
            severity TEXT,
            status TEXT,
            assigned_to TEXT,
            date_reported TEXT,
            date_resolved TEXT,
            FOREIGN KEY (version_id) REFERENCES Software_Versions(version_id)
        );

        CREATE TABLE IF NOT EXISTS Deployments (
            deployment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER,
            environment TEXT,
            deployment_date TEXT,
            deployment_status TEXT,
            FOREIGN KEY (version_id) REFERENCES Software_Versions(version_id)
        );

        CREATE TABLE IF NOT EXISTS Patch_Notes (
            patch_id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER,
            note_title TEXT,
            note_description TEXT,
            FOREIGN KEY (version_id) REFERENCES Software_Versions(version_id)
        );
        """)
        self.conn.commit()

    # --- Software Management ---
    def add_software(self, name):
        self.cursor.execute("INSERT INTO Softwares (name) VALUES (?)", (name,))
        self.conn.commit()

    def get_softwares(self):
        self.cursor.execute("SELECT software_id, name FROM Softwares ORDER BY software_id DESC")
        return self.cursor.fetchall()

    def set_active_software(self, software_id):
        self.active_software_id = software_id

    

    def get_active_software(self):
        return self.active_software_id

    def add_version(self, software_id, version_number, release_date, status, notes):
        self.cursor.execute("""
            INSERT INTO Software_Versions (software_id, version_number, release_date, status, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (software_id, version_number, release_date, status, notes))
        self.conn.commit()

    def get_versions(self, software_id):
        self.cursor.execute("""
            SELECT version_id, version_number, release_date, status, notes
            FROM Software_Versions
            WHERE software_id = ?
            ORDER BY version_id DESC
        """, (software_id,))
        return self.cursor.fetchall()



    def update_version(self, version_id, version_number, release_date, status, notes):
        self.cursor.execute("""
            UPDATE Software_Versions
            SET version_number = ?, release_date = ?, status = ?, notes = ?
            WHERE version_id = ?
        """, (version_number, release_date, status, notes, version_id))
        self.conn.commit()

    def delete_version(self, version_id):
        self.cursor.execute("DELETE FROM Software_Versions WHERE version_id = ?", (version_id,))
        self.conn.commit()


    # --- Close connection ---
    def close(self):
        self.conn.close()

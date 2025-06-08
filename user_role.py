# Python
class User:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.username = username
        self.role = role

    def view_courses(self):
        raise NotImplementedError("Belum ada subclass")

    def edit_courses(self):
        raise NotImplementedError("Belum ada subclass")


class Mahasiswa(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, role="mahasiswa")

    def view_courses(self):
        return "Melihat kursus yang tersedia."

    def edit_courses(self):
        return "Izin untuk mengedit kursus tidak diberikan kepada mahasiswa."


class Instruktur(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, role="instruktur")

    def view_courses(self):
        return "Melihat kursus yang ditugaskan kepada instruktur."

    def edit_courses(self):
        return "Mengedit kursus yang ditugaskan kepada instruktur."


class Admin(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, role="admin")

    def view_courses(self):
        return "Melihat semua kursus yang tersedia di server."

    def edit_courses(self):
        return "Mengedit semua kursus yang tersedia di server."
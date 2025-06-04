# Python
class User:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.username = username
        self.role = role

    def view_courses(self):
        raise NotImplementedError("Subclasses must implement this method")

    def edit_courses(self):
        raise NotImplementedError("Subclasses must implement this method")


class Mahasiswa(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, role="mahasiswa")

    def view_courses(self):
        return "Viewing all available courses."

    def edit_courses(self):
        return "Permission denied! Mahasiswa cannot edit courses."


class Instruktur(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, role="instruktur")

    def view_courses(self):
        return "Viewing all courses assigned to the instructor."

    def edit_courses(self):
        return "Editing courses assigned to the instructor."


class Admin(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, role="admin")

    def view_courses(self):
        return "Viewing all courses on the server."

    def edit_courses(self):
        return "Editing all courses on the server."
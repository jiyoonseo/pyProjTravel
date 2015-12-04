from werkzeug.security import check_password_hash, generate_password_hash


class User(object):

    def __init__(self, email, password, first_name, last_name, from_db):
        if from_db == 1: # from database 
            self.pw_hash = password  
        elif from_db == 0:  # raw data 
            self.set_password(password)

        self.email = email  # user id == user email
        self.fname = first_name
        self.lname = last_name

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    # setter
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
            
    def set_email(self, email):
        self.email = email

    # getter
    def get_email(self):
        return str(self.email)

    def get_fname(self):
        return str(self.fname)

    def get_lname(self):
        return str(self.lname)


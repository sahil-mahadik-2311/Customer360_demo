import bcrypt

class Hashing:

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password , hash_password):

        return  bcrypt.checkpw(plain_password.encode('utf-8'), 
                               hash_password.encode('utf-8'))
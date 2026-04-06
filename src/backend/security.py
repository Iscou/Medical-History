import bcrypt

def hash_password(plain_password):
    """
    Takes a plain text password, adds salt, and returns a secure hash string.
    """
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_password.decode('utf-8')

def verify_password(plain_password, hashed_password_db):
    """
    Compares a plain text attempt against the database hash.
    Returns True if they match, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password_db.encode('utf-8')
    )
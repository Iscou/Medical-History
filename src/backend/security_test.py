import security
h = security.hash_password("1234")
print(f"Hash: {h}")
print(f"Works?: {security.verify_password('1234', h)}")
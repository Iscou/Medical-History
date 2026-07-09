import security
h = security.hash_password("1234")
print(f"Hash: {h}")
print(f"¿Funciona?: {security.verify_password('1234', h)}")
from passlib.hash import pbkdf2_sha256


# Define a function to generate hashed passwords
def generate_hashed_password(pwd: str) -> str:
    # Generate the hashed password using pbkdf2_sha256
    hashed_pwd = pbkdf2_sha256.hash(pwd)
    return hashed_pwd


# Example usage
if __name__ == "__main__":
    # Replace "password123" with the actual password you want to hash
    password = "8Jasn!c"
    hashed_password = generate_hashed_password(password)
    print("Hashed Password:", hashed_password)

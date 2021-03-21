from hashlib import blake2b, sha256


def hash_login(login: str) -> str:
    return sha256(login.encode('utf-8')).hexdigest()


def hash_password(password: str, salt: str):
    # 64 digits is defined in auth table
    hashing_algorithm = blake2b(digest_size=64, key=salt.encode('utf-8'))
    hashing_algorithm.update(password.encode('utf-8'))
    return hashing_algorithm.hexdigest()

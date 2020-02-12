from Crypto.PublicKey import ECC, RSA

class Encryption:
    def __init__(self, pub_key, private):
        self.public_key = pub_key
        self.private = private

    @classmethod
    def create_cert(cls):
        key = RSA.generate(2048)
        with open("key.pem", 'wb') as priv:
            priv.write(key.exportKey('OpenSSH'))
        with open("cert.pem", 'wb') as pub:
            pub.write(key.publickey().exportKey('OpenSSH'))
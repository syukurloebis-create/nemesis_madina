from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

key = Ed25519PrivateKey.generate()
with open('/keys/dev_signing_key.pem', 'wb') as f:
    f.write(key.private_bytes_raw())
print("Key generated successfully")

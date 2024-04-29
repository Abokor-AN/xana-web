from jwcrypto import jwt, jwk

# Génération des clés
key = jwk.JWK.generate(kty='RSA', size=3072)

with open('private_key.pem', 'wb') as f:
    f.write(key.export_to_pem(private_key=True,password=None))

with open('public_key.pem', 'wb') as f:
    f.write(key.export_to_pem(private_key=False))
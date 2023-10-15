import jwt
import requests

if not jwt.algorithms.has_crypto:
    print("No crypto support for JWT, please install the cryptography dependency")

openid_discovery_uri = 'https://login.microsoftonline.com/d2f6c0f3-9039-4a02-9e93-b489a6944a07/v2.0/.well-known/openid-configuration'

jwt_options = {
    "audience": "api://84f6c12a-12bf-4fd0-91bc-2dfb30ecadea",
    "issuer": "https://sts.windows.net/4ea43e8a-132e-48c0-901d-52dd22e7cdf3/"
}


def validate_auth_token(auth_token):
    global jwt_options

    print(auth_token)

    try:
        if auth_token is None:
            raise Exception([401, 'Unauthenticated'])
        openid_discovery_data = requests.get(openid_discovery_uri).json()
        jwks_uri = openid_discovery_data["jwks_uri"]
        jwks = jwt.PyJWKClient(jwks_uri, cache_keys=True, lifespan=360)
        print("OK" + jwks_uri)
        signing_key = jwks.get_signing_key_from_jwt(auth_token)
        data = jwt.decode(auth_token, signing_key.key, algorithms=["RS256"], issuer=jwt_options["issuer"], audience=jwt_options["audience"], options={
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "verify_aud": True,
            "verify_iss": True,
        })
        return data
    except Exception as err:
        print(f"Error: {err}")
        return False


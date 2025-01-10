
import requests



def get_access_token(token_url: str, client_id: str, client_secret: str) -> str:
    """
    Obtiene un token de acceso usando las credenciales del cliente
    """
    response = requests.post(
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "openid profile",
        },
    )
    response.raise_for_status()  # Lanza una excepción si hay error
    return response.json()["access_token"]
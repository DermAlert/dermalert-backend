import requests

VIACEP_URL = "https://viacep.com.br/ws/{cep}/json/"


def fetch_address_from_cep(cep: str) -> dict:
    """
    Retorna um dicionário com os campos do Address ou lança ValueError
    """
    resp = requests.get(VIACEP_URL.format(cep=cep), timeout=3)
    resp.raise_for_status()
    data = resp.json()
    if data.get("erro"):
        raise ValueError("CEP não encontrado")
    return {
        "cep": data["cep"],  # ex: "01001-000"
        "country": "Brasil",
        "state": data["uf"],
        "city": data["localidade"],
        "neighborhood": data["bairro"],
        "street": data["logradouro"],
        "number": None,
        "longitude": None,
        "latitude": None,
    }

import requests


BASE_URL = "https://fipe.parallelum.com.br/api/v2"
TIPO_VEICULO = "motorcycles"


def buscar_marcas():
    response = requests.get(
        f"{BASE_URL}/{TIPO_VEICULO}/brands",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def buscar_modelos(brand_id):
    response = requests.get(
        f"{BASE_URL}/{TIPO_VEICULO}/brands/{brand_id}/models",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def buscar_anos(brand_id, model_id):
    response = requests.get(
        f"{BASE_URL}/{TIPO_VEICULO}/brands/{brand_id}/models/{model_id}/years",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def buscar_preco(brand_id, model_id, year_id):
    response = requests.get(
        f"{BASE_URL}/{TIPO_VEICULO}/brands/{brand_id}/models/{model_id}/years/{year_id}",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
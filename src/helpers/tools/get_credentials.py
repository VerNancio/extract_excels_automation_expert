import json


def get_credentials(reference_name: str) -> dict:
    """
    Retorna dicionárizado as credenciais de login corresponte ao sistema de acesso do cliente informado
    """

    with open('./credentials.json', 'r') as f:
        json_content = f.read()
        json_dicted: dict = json.loads(json_content)

        return json_dicted[reference_name]



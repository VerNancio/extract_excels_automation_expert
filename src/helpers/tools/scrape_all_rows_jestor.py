import requests

from src.constants import JESTOR_BASE_URL


def scrape_all_rows_jestor(
    table_hash: str,
    token: str,
    filters: list | None = None,
    select: list | None = None,
    page_size: int = 100,
) -> list[dict]:
    
    HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    
    print(f'Iniciando scraping dos dados da tabela do Jestor ({table_hash})\n')

    page = 1
    all_records = []

    while True:
        payload = {
            "object_type": table_hash,
            "size": page_size,
            "page": page,
            "token": 'cc0da72ab3741491dec8f2daf2a95bba',
            "filters": {
                "filters": filters or []
            },
            "select": select if select else None
        }

        response = requests.post(
            f'{JESTOR_BASE_URL}/object/list',
            headers=HEADERS,
            json=payload,
        )

        response.raise_for_status()

        data = response.json().get("data", {})
        items = data.get("items", [])
        all_records.extend(items)

        print(f"Página {page}: {len(items)} registros.")

        if not data.get("has_more"):
            print('Todos os registros alvo extraídos.\n')
            break

        page += 1
        
    print(f'Total de registros extraídos da tabela: {len(all_records)}')

    return all_records
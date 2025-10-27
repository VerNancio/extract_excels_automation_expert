# 🐍 Automatização de coleta, tratamento e formatação de dados de atestados 

Esse projeto foi feito dada a necessidade de se automatizar processos de envio de atestados
para o Sharepoint. A ideia foi coletar os dados, tratar, selecionar as informações necessárias,
formatar de acordo com a planilha modelo passada e, por último, gerar planilhas com excels já
prontas para serem postadas no Sharepoint, processo que pode ser feito também automaticamente

Última edit: 27/10/25

## 📂 Estrutura do Projeto

```text
extracao_planilhas_afastados/
├── .venv/
├── data/
├── src/
│   └── main.py
│   └── constants.py
│   └── helpers/
│       └── create_excel/create_excel.py
│       └── treatment/
│           └── dataframe_treatment.py
│       └── tools/
│           └── compare_date_filter.py
│           └── date_formatter.py
│           └── get_credentials.py
│           └── handle_kwargs.py
│           └── store_excels.py
│   └── requesters/
│       └── filetypes_requests.py
│       └── make_requests/
│           └── MakeCloseRequests.py
│           └── MakeJestorRequests.py
│   └── selenium_scrapying/
│           └── greif/greif_selenium_scrapying
│           └── merck/merck_selenium_scrapying.py
│           └── rech/rech_selenium_scrapying.py
│           └── soc/soc_selenium_scrapying.py
│   └── selenium_scrapying
├── requirements.txt
├── credentials.json
├── extract_data.bat
├── run.py
└── README.md
```

## 🚀 Como executar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/VerNancio/extract_excels_automation_expert.git
   cd extract_excels_automation_expert
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # ou
   source .venv/bin/activate     # Linux/Mac
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o projeto (na pasta raiz):**
   ```bash
   python run.py
   ```

## 🧩 Dependências

As principais dependências usadas e suas utilidades:

    - Pandas (orquestrar o tratamento, manipulçaõ e geração dos xlsx)
    - Selenium (operacionalizar por meio de bots web a coleta dos dados)
    - Requests (fazer a requisição de dados de forma direta via HTTP)
    - Numpy (usado em alguns poucos contextos em conjunto com o Pandas)

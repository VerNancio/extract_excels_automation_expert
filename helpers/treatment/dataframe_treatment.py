import numpy as np
import pandas as pd; from pandas import DataFrame, Series
import datetime as dt
import regex as re

from typing import Callable, Type


class DataframeTreatment:

    @staticmethod
    def convert_columns(df: DataFrame) -> DataFrame:

        DT: Type[DataframeTreatment] = DataframeTreatment

        for col, dtype in DT.DEFAULT_COLUMN_TYPES.items():
            if col in df.columns:
                if dtype == 'datetime64[ns]':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                else:
                    df[col] = df[col].astype(dtype)

        return df
    

    @staticmethod
    def treat_and_rename_columns_names(df: DataFrame, client_name: str) -> DataFrame:

        DT: Type[DataframeTreatment] = DataframeTreatment
        df_to_return: DataFrame = df


        df_columns: list[str] = df_to_return.columns.to_list()
        c_names_dict: dict = DT.DEFAULT_COLUMNS_NAMES


        for default_c_name in c_names_dict:

            # IF existe pq key data_lancamento esta como nome, ele serve pra add
            # posteriormente no bloco for abaixo e manter o padrao de dicionarios
            if default_c_name != 'data_lancamento':

                # Acessa o dicionario dos nomes de colunas padrão
                unpatterned_c_name: dict = c_names_dict[default_c_name][client_name]

                # Renomeio das colunas para os nomes padrões
                if unpatterned_c_name in df_columns:
                    df_to_return.rename(columns={unpatterned_c_name: default_c_name}, inplace=True)
                    # df_to_return[default_c_name] = df[unpatterned_c_name]

        return df_to_return

    
    @staticmethod
    def treat_columns(df: DataFrame, client_name: str) -> DataFrame:

        DT: Type[DataframeTreatment] = DataframeTreatment

        df_to_return: DataFrame = df

        """  Dict tendo suas primeiras keys sendo os nomes das coluna com o nome padrão
        As segundas chaves sendo as empresas e seus valores sendo o nome das colunas que vem em seus arquivos
        Ex: c_names_dict['cids']['leroy'] -> 'CID_PRINCIPAL'  """
        c_names_dict: dict = DT.DEFAULT_COLUMNS_NAMES

        c_types_dict: dict[str, type] = DT.NECESSARY_EXPLICIT_TYPE_DECLARATION

        default_column_names: list[str] = c_names_dict.keys()

        columns_to_change_type: list[str] = c_types_dict.keys()
        columns_to_be_treated: list[str] = DT.DEFAULT_TREATEMENTS.keys()


        df_to_return = DT.treat_and_rename_columns_names(df_to_return, client_name)

        # Criação das colunas com dados vazios (pq a planilha básica não tem eles)
        renamed_columns: list[str] = df_to_return.columns.to_list()


        # Itera com os nomes padrões das colunas
        for default_c_name in default_column_names:

            if default_c_name == 'data_lancamento':
                # Data da criação do excel (data da execução desse script)
                df_to_return = DT.add_current_date_column(df_to_return)
                continue

            # Item da chave do dicionario correpondente
            # c_name_value: str | None = c_names_dict[default_c_name][client_name] if default_c_name is not None else None
            c_name_value: str | None = c_names_dict[default_c_name][client_name]

            # Capaz que tenha que mudar o if abaixo pra elif e add um if antes 
            # pra saber se a data de retorno já existe
            if default_c_name == 'dias_afastamento' and c_name_value is not None:
                # Calcula a data de retorno baseado na quant de dias afastado
                # print('!' *100)
                print(default_c_name)
                df_to_return = DT.add_return_date_column(df_to_return)

            elif default_c_name not in renamed_columns and default_c_name != 'data_retorno':
                # print('?' *100)
                print(default_c_name)

                # Cria uma coluna (se não existir) com nome padrão com valores nulo
                df_to_return[default_c_name] = np.nan

            # if default_c_name in columns_to_change_type:
            #     # Muda o tipo da coluna
            #     df_to_return[default_c_name] = DT.change_column_type(df_to_return, default_c_name)

            if default_c_name in columns_to_be_treated:
                # Trata os dados
                df_to_return[default_c_name] = DT.treat_column(df_to_return, default_c_name)


        # Temporario -- tentativa de salvar o datetime com a data somente
        df_to_return['data_inicio'] = pd.to_datetime(df_to_return['data_inicio'], format='%d/%m/%Y', errors='coerce')
        df_to_return['data_inicio'] = df_to_return['data_inicio'].dt.strftime('%d/%m/%Y')
        
        df_to_return['data_retorno'] = pd.to_datetime(df_to_return['data_retorno'], format='%d/%m/%Y', errors='coerce')
        df_to_return['data_retorno'] = df_to_return['data_retorno'].dt.strftime('%d/%m/%Y')

        df_to_return.loc[pd.isna(df_to_return['data_retorno']), 'data_retorno'] = dt.datetime(1999, 12, 31).strftime('%d/%m/%Y')

        return df_to_return[list(default_column_names)]
    

    @staticmethod
    def add_columns_names(df: DataFrame) -> DataFrame:
        """
        Adiciona os nomes de cabeçalho de cada coluna, no caso de não existirem
        """



    @staticmethod
    def add_current_date_column(df: DataFrame) -> Series:
        """
        Adiciona a coluna de data_lancamento com a data de hoje (quando idealmente será lançado no sharepoint)
        """
        df_to_return = df
        df_to_return['data_lancamento'] = dt.date.today().strftime("%d/%m/%Y")

        return df_to_return
    

    @staticmethod
    def add_return_date_column(df: DataFrame) -> DataFrame:
        # Garante que a coluna existe
        if 'dias_afastamento' not in df.columns:
            raise KeyError("A coluna 'dias_afastamento' não existe no DataFrame")

        # Converte para numérico, valores inválidos viram NaN
        df['dias_afastamento'] = pd.to_numeric(df['dias_afastamento'], errors='coerce')

        # Converte datas (mais tolerante)
        df['data_inicio'] = pd.to_datetime(df['data_inicio'], errors='coerce', dayfirst=True)

        # Data caso nao haja data de retorno
        return_date_without_value = dt.datetime(1999, 12, 31)

        # Cria a nova coluna
        df['data_retorno'] = df.apply(
            lambda row: row['data_inicio'] + dt.timedelta(days=int(row['dias_afastamento']))
            if pd.notnull(row['dias_afastamento'])
            else return_date_without_value,
            axis=1
        )

        return df
    
    
    @staticmethod
    def change_column_type(df: DataFrame, column_name: str) -> DataFrame:
        """
        Aplica uma mudança de tipo baseado no dicionário 
        de declaração de tipos explicita; Ex: cpf (float64) -> cpf (object/string)
        """
        c_types_dict: dict[str, type] = DataframeTreatment.NECESSARY_EXPLICIT_TYPE_DECLARATION

        return df[column_name].astype(c_types_dict[column_name])
    
    
    @staticmethod
    def treat_column(df: DataFrame, column_name: str) -> DataFrame:
        """
        Aplica os tratamentos por meio da função lambdas indicadas pelas keys do dict
        Ex (cpf): 353.280.640-11 -> 35328064011
        """
        # if column_name == 'cpf':
        #     df.loc[pd.isna(df['cpf'])].dropna(subset=['cpf'], inplace=True)
        #     # loc[pd.isna(df_to_return['data_retorno']), 'data_retorno']

        return df[column_name].apply(DataframeTreatment.DEFAULT_TREATEMENTS[column_name])

    NECESSARY_COLUMNS: list[str] = ['cpf', 'data_inicio', 'data_fim', 'data_lancamento', 'nome_funcionario']

    NECESSARY_EXPLICIT_TYPE_DECLARATION: dict[str] = {
        'cpf': str,
    }

    DEFAULT_TREATEMENTS: dict[str, Callable[[str], str]] = {
        'cids': lambda cid: re.sub(r"[.-]", "", str(cid)) if type(cid) != float else '',
        # 'cpf': lambda cpf: re.sub(r"[.-]", "", str(cpf)).zfill(11) if not pd.isna(cpf) or str(cpf).lower() != 'nan' else '',
        'cpf': lambda cpf: re.sub(r"[.-]", "", str(cpf)).zfill(11) if pd.notna(cpf) else ''
        # 'cpf': lambda cpf: re.sub(r"[.-]", "", str(cpf)).zfill(11) if not pd.isna(cpf) else '',
    }

    DEFAULT_COLUMNS_NAMES: dict[dict] = {
        'cids': {
            'greif': 'Código(s) CID',
            'rech': '', 
            'leroy': 'CID_ADICIONAL', 'pluri': 'CID_PRINCIPAL'
        },
        'cids_descricao': {
            'greif': '',    
            'rech': '', 
            'leroy': 'DESCRICAO_CID_ADICIONAL', 'pluri': 'DESCRICAO_CID'
        },
        'cpf': {
            'greif': 'CPF do Funcionário',
            'rech': 'CPF', 
            'leroy': 'CPF', 'pluri': 'CPF'
        },
        'dias_afastamento': {
            'greif': 'Prazo',
            'rech': 'Quantidade de Dias de Afastamento',
            'leroy': None, 'pluri': None
        },
        'data_inicio': {
            'greif': 'Data Abertura',
            'rech': 'Data Inicial do afastamento', 
            'leroy': 'DT_INICIO_ATESTADO', 'pluri': 'DT_INICIO_ATESTADO'
        },
        'data_retorno': {
            'greif': 'Data Encerramento',
            'rech': '', 
            'leroy': 'DT_FIM_ATESTADO', 'pluri': 'DT_FIM_ATESTADO'
        },
        'data_lancamento': None,
            # 'leroy': 'DT_CRIACAO', 'pluri': 'DT_CRIACAO' ########### DATA EM QUE SERA POSTO NA PLANILHA
        'estado_prestador': {
            'greif': 'Estado',
            'rech': '', 
            'leroy': '', 'pluri': ''
        },
        'hora_fim': {
            'greif': '',
            'rech': '', 
            'leroy': 'HORA_FIM_ATESTADO', 'pluri': 'HORA_FIM_ATESTADO'
        },
        'hora_inicio': {
            'greif': '',
            'rech': '', 
            'leroy': 'HORA_INICIO_ATESTADO', 'pluri': 'HORA_INICIO_ATESTADO'
        },
        'identificador_prestador': {
            'greif': '',
            'rech': '', 
            'leroy': '', 'pluri': ''
        },
        'local': {
            'greif': 'Empresa',
            'rech': 'Filial', 
            'leroy': '', 'pluri': ''
        },
        'nome_funcionario': {
            'greif': 'Funcionário',
            'rech': 'Colaborador', 
            'leroy': 'NOME_FUNCIONARIO', 'pluri': 'NOME_FUNCIONARIO'
        },
        'nome_prestador': {
            'greif': 'Nome do Médico',
            'rech': '', 
            'leroy': '', 'pluri': ''
        },
        'tipo': {
            'greif': '',
            'rech': '', 
            'leroy': '', 'pluri': ''
        },
        'codigo_tipo': {
            'greif': '',
            'rech': '', 
            'leroy': '', 'pluri': ''
        },
        'tipo_prestador': {
            'greif': '',
            'rech': '', 
            'leroy': '', 'pluri': ''
        },
        'matricula': {
            'greif': 'Matrícula do Funcionário',
            'rech': 'Cadastro', 
            'leroy': 'MATRICULA_FUNC', 'pluri': 'MATRICULA_FUNC'
        },
        'crm': {
            'greif': 'Atestado Crm',
            'rech': '', 
            'leroy': '', 'pluri': ''
        }
    }
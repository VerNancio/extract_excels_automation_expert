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
    def treat_columns(df: DataFrame, enterprise_name: str) -> DataFrame:

        DT: Type[DataframeTreatment] = DataframeTreatment

        df_to_return: DataFrame = DataFrame()
        df_columns: list[str] = df.columns.to_list()

        """  Dict tendo suas primeiras keys sendo os nomes de coluna padrão
        As segundas chaves sendo as empresas e seus valores sendo o nome das colunas que vem em seus arquivos
        Ex: c_names_dict['cids']['leroy'] -> 'CID_PRINCIPAL'  """
        c_names_dict: dict = DT.DEFAULT_COLUMNS_NAMES

        c_types_dict: dict[str, type] = DT.NECESSARY_EXPLICIT_TYPE_DECLARATION

        default_column_names: list[str] = c_names_dict.keys()

        columns_to_change_type: list[str] = c_types_dict.keys()
        columns_to_be_treated: list[str] = DT.DEFAULT_TREATEMENTS.keys()

        for default_c_name in c_names_dict:

            # IF existe pq key data_lancamento esta como nome, ele serve pra add
            # posteriormente no bloco for abaixo e manter o padrao de dicionarios
            if default_c_name != 'data_lancamento':
                unpatterned_c_name: dict = c_names_dict[default_c_name][enterprise_name]

                # Renomeio das colunas para os nomes padrões
                if unpatterned_c_name in df_columns:
                    df_to_return[default_c_name] = df[unpatterned_c_name]

            # Criação das colunas com dados vazios (pq a planilha básica não tem eles)
            renamed_columns: list[str] = df_to_return.columns.to_list()

            # Itera com os nomes padrões das colunas
            for default_c_name in default_column_names:
                    
                if default_c_name == 'data_lancamento':
                    df_to_return = DT.add_current_date_column(df_to_return)

                elif default_c_name not in renamed_columns:
                    # Cria uma coluna (se não existir) com nome padrão com valores nulo
                    df_to_return[default_c_name] = np.nan

                if default_c_name in columns_to_change_type:
                    # Muda o tipo da coluna
                    df_to_return[default_c_name] = DT.change_column_type(df_to_return, default_c_name)

                if default_c_name in columns_to_be_treated:
                    # Trata os dados
                    df_to_return[default_c_name] = DT.treat_column(df_to_return, default_c_name)

        return df_to_return


    @staticmethod
    def add_current_date_column(df: DataFrame) -> DataFrame:
        """
        Adiciona a coluna de data_lancamento com a data de hoje (quando idealmente será lançado no sharepoint)
        """
        df_to_return = df

        today = dt.date.today()
        df_to_return['data_lancamento'] = today.strftime("%d/%m/%Y")

        return df_to_return
    
    
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
        return df[column_name].apply(DataframeTreatment.DEFAULT_TREATEMENTS[column_name])


    NECESSARY_COLUMNS: list[str] = ['cpf', 'data_inicio', 'data_fim', 'data_lancamento', 'nome_funcionario']

    NECESSARY_EXPLICIT_TYPE_DECLARATION: dict[str] = {
        'cpf': str,
    }

    DEFAULT_TREATEMENTS: dict[str, Callable[[str], str]] = {
        'cids': lambda cid: re.sub(r"[.-]", "", str(cid)) if type(cid) != float else '',
        'cpf': lambda cpf: re.sub(r"[.-]", "", str(cpf)).zfill(11),
    }

    DEFAULT_COLUMNS_NAMES: dict[dict] = {
        'cids': {
            'leroy': 'CID_PRINCIPAL', 'pluri': 'CID_PRINCIPAL'
        },
        'cids_descricao': {
            'leroy': 'DESCRICAO_CID', 'pluri': 'DESCRICAO_CID'
        },
        'cpf': {
            'leroy': 'CPF', 'pluri': 'CPF'
        },
        'data_retorno': {
            'leroy': 'DT_FIM_ATESTADO', 'pluri': 'DT_FIM_ATESTADO'
        },
        'data_inicio': {
            'leroy': 'DT_INICIO_ATESTADO', 'pluri': 'DT_INICIO_ATESTADO'
        },
        'data_lancamento': None,
            # 'leroy': 'DT_CRIACAO', 'pluri': 'DT_CRIACAO' ########### DATA EM QUE SERA POSTO NA PLANILHA
        'estado_prestador': {
            'leroy': '', 'pluri': ''
        },
        'hora_fim': {
            'leroy': 'HORA_FIM_ATESTADO', 'pluri': 'HORA_FIM_ATESTADO'
        },
        'hora_inicio': {
            'leroy': 'HORA_INICIO_ATESTADO', 'pluri': 'HORA_INICIO_ATESTADO'
        },
        'identificador_prestador': {
            'leroy': '', 'pluri': ''
        },
        'local': {
            'leroy': '', 'pluri': ''
        },
        'nome_funcionario': {
            'leroy': 'NOME_FUNCIONARIO', 'pluri': 'NOME_FUNCIONARIO'
        },
        'nome_prestador': {
            'leroy': '', 'pluri': ''
        },
        'tipo': {
            'leroy': '', 'pluri': ''
        },
        'codigo_tipo': {
            'leroy': '', 'pluri': ''
        },
        'tipo_prestador': {
            'leroy': '', 'pluri': ''
        },
        'matricula': {
            'leroy': 'MATRICULA_FUNC', 'pluri': 'MATRICULA_FUNC'
        }
    }
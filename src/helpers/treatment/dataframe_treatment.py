import numpy as np
import pandas as pd; from pandas import DataFrame, Series
import datetime as dt
import regex as re

from typing import Callable, Type

class DataframeTreatment:

    # @staticmethod
    # def convert_columns(df: DataFrame) -> DataFrame:

    #     DT: Type[DataframeTreatment] = DataframeTreatment

    #     for col, dtype in DT.DEFAULT_COLUMN_TYPES.items():
    #         if col in df.columns:
    #             if dtype == 'datetime64[ns]':
    #                 df[col] = pd.to_datetime(df[col], errors='coerce')
    #             else:
    #                 df[col] = df[col].astype(dtype)

    #     return df

    
    @staticmethod
    def treat_df(df: DataFrame, client_name: str) -> DataFrame:
        
        DT: Type[DataframeTreatment] = DataframeTreatment
        print(df.columns)

        df_to_return: DataFrame = df

        """  Dict tendo suas primeiras keys sendo os nomes das coluna com o nome padrão
        As segundas chaves sendo as empresas e seus valores sendo o nome das colunas que vem em seus arquivos
        Ex: c_names_dict['cids']['leroy'] -> 'CID_PRINCIPAL'  """
        c_names_dict: dict = DT.DEFAULT_COLUMNS_NAMES

        # c_types_dict: dict[str, type] = DT.NECESSARY_EXPLICIT_TYPE_DECLARATION
        # columns_to_change_type: list[str] = c_types_dict.keys()

        default_column_names: list[str] = c_names_dict.keys()
        columns_to_be_treated: list[str] = DT.DEFAULT_TREATEMENTS.keys()

        df_to_return = DT.rename_columns_names(df_to_return, client_name)
        df_to_return = DT.change_column_types(df_to_return)
        
        # Criação das colunas com dados vazios (pq a planilha básica não tem eles)
        renamed_columns: list[str] = df_to_return.columns.to_list()



        # Itera com os nomes padrões das colunas
        for default_c_name in default_column_names:
            
            # Item da chave do dicionario correpondente
            # c_name_value: str | None = c_names_dict[default_c_name][client_name] if default_c_name is not None else None
            c_name_value: str | None = c_names_dict[default_c_name][client_name]

            # Se a coluna deve ser tratada e o c_name_value é diferente de nulo, 
            # ou seja, ela existe, executa o tratamento de coluna
            if default_c_name in columns_to_be_treated:
                if c_name_value is None:
                    df_to_return[default_c_name] = ''
                else:
                    df_to_return[default_c_name] = DT.apply_treatments_column(df_to_return, default_c_name)

            if default_c_name == 'data_lancamento':
                # Data da criação do excel (data da execução desse script)
                # df_to_return = DT.add_current_date_column(df_to_return)
                df_to_return['data_lancamento'] = dt.date.today().strftime('%d/%m/%Y') 
                continue

            # Capaz que tenha que mudar o if abaixo pra elif e add um if antes 
            # pra saber se a data de retorno já existe

            # if default_c_name not in renamed_columns and default_c_name != 'data_retorno': # antigo e funcional
            if default_c_name not in renamed_columns:
                # Cria uma coluna (se não existir) com nome padrão com valores nulo
                df_to_return[default_c_name] = np.nan

            if (default_c_name == 'dias_afastamento' and c_name_value is not None) or client_name == 'rech':
                # Calcula a data de retorno baseado na quant de dias afastado
                df_to_return = DT.add_return_date_column(df_to_return)
            
            if default_c_name == 'tipo':
                
                if df_to_return['tipo'].empty:
                    # Acrescenta 'afastamento e declaração de horas' a todas a colunas do tipo
                    df_to_return['tipo'] = ''
                    
                    
        # Temporario (que vai ficar por hora) -- tentativa de salvar o datetime com a data somente
        df_to_return['data_inicio'] = pd.to_datetime(df_to_return['data_inicio'], format='%d/%m/%Y', errors='coerce')
        df_to_return['data_inicio'] = df_to_return['data_inicio'].dt.strftime('%d/%m/%Y')
        
        df_to_return['data_retorno'] = pd.to_datetime(df_to_return['data_retorno'], format='%d/%m/%Y', errors='coerce')
        df_to_return['data_retorno'] = df_to_return['data_retorno'].dt.strftime('%d/%m/%Y')
        
        # df_to_return.loc[pd.isna(df_to_return['data_retorno']), 'data_retorno'] = dt.datetime(9999, 12, 31).strftime('%d/%m/%Y')

        # Filtra somente as colunas relevantes pro modelo (pq tem umas colunas a mais que não tem na planilha modelo, mas que tbm não tem valor nenhum, então n tem problema deixar elas de fora)
        df_to_return = df_to_return[DT.ALL_RELEVANT_MODEL_COLUMNS]
        
        # Adiciona as colunas que são necessárias pra planilha modelo, mas que não tem valor nenhum (pq a planilha básica não tem eles)
        df_to_return = DT.add_useless_columns(df_to_return)
        
        return df_to_return


    @staticmethod
    def rename_columns_names(df: DataFrame, client_name: str) -> DataFrame:

        DT: Type[DataframeTreatment] = DataframeTreatment
        df_to_return: DataFrame = df.copy()  # evita efeitos colaterais

        df_columns: list[str] = df_to_return.columns.to_list()
        c_names_dict: dict = DT.DEFAULT_COLUMNS_NAMES

        for default_c_name in c_names_dict:
            if default_c_name == 'data_lancamento':
                continue

            unpatterned_c_name: str = c_names_dict[default_c_name][client_name]
            if unpatterned_c_name == '=':
                if default_c_name not in df_to_return.columns:
                    df_to_return[default_c_name] = ''
            elif unpatterned_c_name in df_to_return.columns:
                df_to_return[default_c_name] = df_to_return.pop(unpatterned_c_name)
            else:
                if default_c_name not in df_to_return.columns:
                    df_to_return[default_c_name] = ''                    
                    
        return df_to_return
                    

    @staticmethod
    def change_column_types(df: DataFrame) -> DataFrame:

        c_types_dict: dict = DataframeTreatment.NECESSARY_EXPLICIT_TYPE_DECLARATION
        
        for c_name in c_types_dict.keys():
            if c_name in df.columns:
                df[c_name] = df[c_name].astype(c_types_dict[c_name])
                
        return df
    

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

        default_null_date = pd.Timestamp("9999-12-31")
        
        print(df['data_inicio'])

        if 'data_inicio' not in df.columns:
            raise KeyError("A coluna 'data_inicio' não existe no DataFrame")
        
        # Garantir coluna data_retorno
        if 'data_retorno' not in df.columns.to_list():
            df['data_retorno'] = pd.NA

        # Garantir coluna dias_afastamento
        if 'dias_afastamento' not in df.columns.to_list():
            df['dias_afastamento'] = pd.NA

        
        # Extrai apenas número
        df['dias_afastamento'] = (
            df['dias_afastamento']
            .astype(str)
            .str.extract(r'(\d+)')[0]
            .pipe(pd.to_numeric, errors='coerce')
        )

        # Converte datas
        df['data_inicio'] = pd.to_datetime(df['data_inicio'], dayfirst=True, errors='coerce')
        # df['data_inicio'] = df['data_inicio'].dt.strftime('%d/%m/%Y')
        
        df['data_retorno'] = pd.to_datetime(df['data_retorno'], dayfirst=True, errors='coerce')
        # df['data_retorno'] = df['data_retorno'].dt.strftime('%d/%m/%Y')
        
        # Máscara para calcular retorno
        mask_calculate = (
            df['data_retorno'].isna() &
            df['dias_afastamento'].notna() &
            df['data_inicio'].notna()
        )

        df.loc[mask_calculate, 'data_retorno'] = (
            df.loc[mask_calculate, 'data_inicio'] +
            pd.to_timedelta(df.loc[mask_calculate, 'dias_afastamento'], unit='D')
        )

        # Linhas ainda sem retorno → padrão
        df['data_retorno'] = df['data_retorno'].fillna(default_null_date)

        # Formatar saída
        df['data_inicio'] = df['data_inicio'].dt.strftime('%d/%m/%Y')
        df['data_retorno'] = df['data_retorno'].dt.strftime('%d/%m/%Y')

        return df


    @staticmethod
    def add_useless_columns(df: DataFrame) -> DataFrame:
        """_Adiciona ao df colunas que são necessárias na planilha \
            pra funcionar no BI, mas que não precisam de valores_

        Args:
            df (DataFrame): _description_

        Returns:
            DataFrame: _description_
        """
        
        columns_to_add = [
            'codigo_situacao',
            'data_atualizacao',
            'dias_justificados',
            'dose_vacina',
            'formato_data',
            'fuso_horario',
            'id_atestado',
            'identificador_funcionario',
            'minutos',
            'minutos_deslocamento_antes',
            'minutos_deslocamento_depois',
            'nome_vacina',
            'observacao',
            'protocolo',
            'status',
            'tipo_identificador'
        ]

        for c in columns_to_add:
            df[c] = pd.NA
            
        return df
        
    

    # @staticmethod
    # def drop_nulls(df: DataFrame) -> DataFrame:

    #     # non_null_columns: list[str] = DataframeTreatment.NECESSARY_NON_NULL_VALUES
    #     # df_to_return = df

    #     # for col in non_null_columns:
    #     #     df_to_return = df_to_return[df_to_return[col].notna() & (df_to_return[col].astype(str).str.strip() != "")]
    #     return df
    #     return df_to_return
    
    
    # @staticmethod
    # def change_column_type(df: DataFrame, column_name: str) -> DataFrame:
    #     """
    #     Aplica uma mudança de tipo baseado no dicionário 
    #     de declaração de tipos explicita; Ex: cpf (float64) -> cpf (object/string)
    #     """
    #     c_types_dict: dict[str, type] = DataframeTreatment.NECESSARY_EXPLICIT_TYPE_DECLARATION

    #     return df[column_name].astype(c_types_dict[column_name])
    
    # @staticmethod
    # def treat_by_type(column: Series):

    #     regex = r'[^a-zA-Z0-9\s]'
    #     # máscara: True somente para elementos que são str (np.nan / None / pd.NA ficam False)
    #     mask = column.map(lambda x: isinstance(x, str))

    #     # se não há strings, retorna a coluna original
    #     if not mask.any():
    #         return column

    #     col = column.copy()
    #     # aplica .str.replace apenas nas linhas que são strings
    #     col.loc[mask] = col.loc[mask].str.replace(regex, '', regex=True)
    #     return col

    
    @staticmethod
    def apply_treatments_column(df: DataFrame, column_name: str) -> DataFrame:
        """
        Aplica os tratamentos por meio da função lambdas indicadas pelas keys do dict
        Ex (cpf): 353.280.640-11 -> 35328064011
        """
        # if column_name == 'cpf':
            # df.loc[pd.isna(df['cpf'])].dropna(subset=['cpf'], inplace=True)
            # loc[pd.isna(df_to_return['data_retorno']), 'data_retorno']
            
        if column_name == 'identificador_prestador':
            df['identificador_prestador'] = df['identificador_prestador'].astype(str)
            df['identificador_prestador'] = df['identificador_prestador'].str.replace(r".0", "", regex=True)
            
        if column_name == 'cids':
            
            df_cids = pd.read_csv('./data/CID-10.csv', dtype=str, sep=';', encoding="latin1")
            CID_SET: set[str] = set(df_cids['SUBCAT'].str.upper().str.strip())
            
            # Substitui valores NaN reais ou string "nan" por string vazia
            # df.loc[df['cids'].isna() | (df['cids'].astype(str).str.lower() == "nan"), 'cids'] = ""
            df.loc[df['cids'].isna(), 'cids'] = ''

            # Exemplo extra: se quiser normalizar "s/c" também
            # df.loc[df['cids'].astype(str).str.lower() == "s/c", 'cids'] = ""
            
            others_invalid_values: set[str] = {
                'none', 'nan', 's/c', 'sem cid', 
                'sem código', 'sem código cid', 'sem informação', 
                'sem dados', 'não informado', 'n/a'
            }
            
            df.loc[df['cids'].astype(str).str.lower().isin(others_invalid_values), 'cids'] = ''
            
            # Tratamento pra comparação
            df['cids'] = df['cids'].str.extract(r'([A-Z]\d{2,3})')
            df.loc[df['cids'].astype(str).str.lower().isin(CID_SET), 'cids'] = ''
            
            # Caso haja multiplos cids em uma mesma célula, extrai somente o primeiro que é o mais relevante (ex: "G560 / G561" -> "G560")
            df["cids"] = (
                df["cids"]
                .astype(str)
                .str.upper()
                .str.extract(r'([A-Z]\d{2}\.?\d?)')[0]
            )
            
        return df[column_name].apply(DataframeTreatment.DEFAULT_TREATEMENTS[column_name])


    NECESSARY_MODEL_COLUMNS: list[str] = ['cpf', 'data_inicio', 'data_fim', 'data_lancamento', 'nome_funcionario']
    ALL_RELEVANT_MODEL_COLUMNS: list[str] = [
                                    'cids', 'cids_descricao', 'cpf', 'data_retorno', 
                                    'data_inicio', 'data_lancamento', 'estado_prestador', 
                                    'hora_fim', 'hora_inicio', 'identificador_prestador', 
                                    'local', 'nome_funcionario', 'nome_prestador', 'tipo', 
                                    'codigo_tipo', 'tipo_prestador', 'matricula'
                                ]

    NECESSARY_EXPLICIT_TYPE_DECLARATION: dict[str] = {
        'cpf': str,
        'nome_funcionario': str,
        'cids': str,
        'identificador_prestador': str,
        'matricula': str
    }

    NECESSARY_NON_NULL_VALUES: list[str] = [
        'cpf',
        'data_inicio'
    ]

    DEFAULT_TREATEMENTS: dict[str, Callable[[str], str]] = {
        'cids': lambda cid: re.sub(r"[.-]", "", str(cid)) 
                            if type(cid) != float and pd.notna(cid) and str(cid).lower().strip() not in ['none', 'nan'] 
                            else '',
                            # if type(cid) != float and cid != 'nan' else '',
        'cids_descricao': lambda desc: re.sub(r'[^a-zA-Z0-9\s]', '', str(desc)) if pd.notna(desc) else desc,
        'codigo_tipo': lambda tipo: re.sub(r'[^a-zA-Z0-9\s]', ' ', str(tipo)) if pd.notna(tipo) else tipo,
        'nome_funcionario': lambda name: str(name).lower()
                                         if pd.notna(name) and str(name).strip().lower() not in ['nan', 'none', '']
                                         else '',
        'hora_inicio': lambda hora: hora.strip('Hh ') if pd.notna(hora) else '',

        'hora_fim': lambda hora: str(hora).strip('Hh ') if pd.notna(hora) else '',
        'cpf': lambda cpf: (
            re.sub(r"[.-]", "", str(cpf)).zfill(11)
            if pd.notna(cpf) and str(cpf).strip().lower() not in ['nan', 'none', '']
            else ''
        ),
        'identificador_prestador': lambda x: re.sub(r"[.-]", "", str(x)) if pd.notna(x) else x
    }

    DEFAULT_COLUMNS_NAMES: dict[dict] = {
    'cids': {
        'pergoletta': 'cid_1',
        'fabitos': 'cid_1',
        'workon': 'CID10',
        'greif': 'Código(s) CID',
        'merck': 'CID',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'CIDs Adicionais',
        # 'pluri': 'CIDs Adicionais',
        # 'viva': 'CIDs Adicionais',
        'leroy': 'CID',
        'pluri': 'CID',
        'viva': 'CID',
    },

    'cids_descricao': {
        'pergoletta': None,
        'fabitos': None,
        'workon': None,
        'greif': None,
        'merck': '=',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Descrição do Cid Adicional',
        # 'pluri': 'Descrição do Cid Adicional',
        # 'viva': 'Descrição do Cid Adicional',
        'leroy': None,
        'pluri': None,
        'viva': None,
    },

    'cpf': {
        'pergoletta': 'cpf_1',
        'fabitos': 'cpf_2',
        'workon': 'CPF',
        'greif': 'CPF do Funcionário',
        'merck': 'CPF',
        'rech': 'CPF',
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        'leroy': 'CPF',
        'pluri': 'CPF',
        'viva': 'CPF',
    },

    'nome_funcionario': {
        'pergoletta': 'nome_do_colaborador_1',
        'fabitos': 'nome_do_colaborador_1',
        'workon': 'Nome',
        'greif': 'Funcionário',
        'merck': 'Nome',
        'rech': 'Colaborador',
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Funcionário',
        # 'pluri': 'Funcionário',
        # 'viva': 'Funcionário',
        'leroy': '=',
        'pluri': '=',
        'viva': '=',
    },

    'matricula': {
        'pergoletta': None,
        'fabitos': None,
        'workon': 'Matricula RH',
        'greif': 'Matrícula do Funcionário',
        'merck': 'Matrícula',
        'rech': 'Cadastro',
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Matrícula',
        # 'pluri': 'Matrícula',
        # 'viva': 'Matrícula',
        'leroy': 'CODIGOFUNCIONARIO',
        'pluri': 'CODIGOFUNCIONARIO',
        'viva': 'CODIGOFUNCIONARIO',
    },

    'dias_afastamento': {
        'pergoletta': 'duracao_do_atestado',
        'fabitos': 'duracao_do_atestado',
        'workon': None,
        'greif': 'Quantidade de dias',
        'merck': 'Dias Perdidos',
        'rech': 'Quantidade de Dias de Afastamento',
        'coop': None,
        'bimbo': None,
        'copa': None,
        # 'leroy': 'Dias Afastados',
        # 'pluri': 'Dias Afastados',
        # 'viva': 'Dias Afastados',
        'leroy': 'DIASAFASTADOS',
        'pluri': 'DIASAFASTADOS',
        'viva': 'DIASAFASTADOS',
    },

    'data_inicio': {
        'pergoletta': 'data_inicial',
        'fabitos': 'data_inicial',
        'workon': 'Inicio',
        'greif': 'Atestado Data Inicio',
        'merck': 'Data Início',
        'rech': 'Data Inicial do afastamento',
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Início',
        # 'pluri': 'Início',
        # 'viva': 'Início',
        'leroy': 'INICIO',
        'pluri': 'INICIO',
        'viva': 'INICIO',
    },

    'data_retorno': {
        'pergoletta': 'data_final',
        'fabitos': 'Data Término',
        'workon': 'Termino',
        'greif': 'Data Encerramento',
        'merck': 'Data Término',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Fim',
        # 'pluri': 'Fim',
        # 'viva': 'Fim',
        'leroy': 'RETORNO',
        'pluri': 'RETORNO',
        'viva': 'RETORNO',
    },

    'data_lancamento': {
        'pergoletta': None,
        'fabitos': None,
        'workon': None,
        'greif': None,
        'merck': None,
        'rech': None,
        'coop': None,
        'bimbo': None,
        'copa': None,
        # 'leroy': None,
        # 'pluri': None,
        # 'viva': None,
        'leroy': 'DATADECRIACAO',
        'pluri': 'DATADECRIACAO',
        'viva': 'DATADECRIACAO',
    },

    'hora_inicio': {
        'pergoletta': '=',
        'fabitos': '=',
        'workon': None,
        'greif': '=',
        'merck': 'Hora Início',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Hora Inicial',
        # 'pluri': 'Hora Inicial',
        # 'viva': 'Hora Inicial',
        'leroy': 'HORAINICIAL',
        'pluri': 'HORAINICIAL',
        'viva': 'HORAINICIAL',
    },

    'hora_fim': {
        'pergoletta': '=',
        'fabitos': '=',
        'workon': None,
        'greif': '=',
        'merck': 'Hora Término',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Hora Final',
        # 'pluri': 'Hora Final',
        # 'viva': 'Hora Final',
        'leroy': 'HORAFINAL',
        'pluri': 'HORAFINAL',
        'viva': 'HORAFINAL',
    },

    'nome_prestador': {
        'pergoletta': 'medico',
        'fabitos': 'medico',
        'workon': 'Medico_Nome',
        'greif': 'Nome do Médico',
        'merck': 'Responsável',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Médico Solicitante',
        # 'pluri': 'Médico Solicitante',
        # 'viva': 'Médico Solicitante',
        'leroy': 'MEDICO',
        'pluri': 'MEDICO',
        'viva': 'MEDICO',
    },

    'identificador_prestador': {
        'pergoletta': None,
        'fabitos': None,
        'workon': 'Medico_Numero',
        'greif': 'Atestado Crm',
        'merck': 'Registro',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Conselho de Classe',
        # 'pluri': 'Conselho de Classe',
        # 'viva': 'Conselho de Classe',
        'leroy': 'CONSELHODECLASSE',
        'pluri': 'CONSELHODECLASSE',
        'viva': 'CONSELHODECLASSE',
    },

    'estado_prestador': {
        'pergoletta': None,
        'fabitos': None,
        'workon': None,
        'greif': 'Estado',
        'merck': 'Regional',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'UF',
        # 'pluri': 'UF',
        # 'viva': 'UF',
        'leroy': 'ESTADO',
        'pluri': 'ESTADO',
        'viva': 'ESTADO',
    },

    'local': {
        'pergoletta': 'local_do_exame',
        'fabitos': 'local_do_exame',
        'workon': 'LOCAL DE EMISSÃO',
        'greif': 'Empresa',
        'merck': 'Unidade',
        'rech': 'Filial',
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Unidade',
        # 'pluri': 'Unidade',
        # 'viva': 'Unidade',
        'leroy': 'LOCAL',
        'pluri': 'LOCAL',
        'viva': 'LOCAL',
    },

    'tipo': {
        'pergoletta': 'tipo_de_atestado',
        'fabitos': 'tipo_de_atestado',
        'workon': None,
        'greif': None,
        'merck': None,
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        # 'leroy': 'Tipo Licença',
        # 'pluri': 'Tipo Licença',
        # 'viva': 'Tipo Licença',
        'leroy': 'TIPOLICENCA',
        'pluri': 'TIPOLICENCA',
        'viva': 'TIPOLICENCA',
    },

    'codigo_tipo': {
        'pergoletta': None,
        'fabitos': None,
        'workon': None,
        'greif': None,
        'merck': None,
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        'leroy': None,
        'pluri': None,
        'viva': None,
    },

    'tipo_prestador': {
        'pergoletta': None,
        'fabitos': None,
        'workon': 'Medico_Tipo',
        'greif': None,
        'merck': 'Conselho',
        'rech': None,
        'coop': '=',
        'bimbo': '=',
        'copa': '=',
        'leroy': None,
        'pluri': None,
        'viva': None,
    },
}
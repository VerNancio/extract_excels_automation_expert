import os
import base64
import hashlib
import datetime
from datetime import timezone
import uuid
from zoneinfo import ZoneInfo

from io import StringIO
import requests as req

import pandas as pd; from pandas import DataFrame, Series

from ...helpers.tools.date_formatter import DateFormatter
from ...helpers.tools.compare_date_filter import CompareDateFilter    

from ...helpers.tools.get_credentials import get_credentials



class MakeSocRequests:
    
    client_name: str
    credentials: dict[str, str]
    expires_in_seconds: int
    
    
    def __init__(self, client_name: str, expires_in_seconds: int = 60):
        """_summary_

        Args:
            expires_in_seconds (int): _segundos até xml expirar; default é 60; max é 120_
            client_name (str): _nome da empresa cliente; "leroy", "pluri" ou "leroy"_
        """
        
        self.client_name = client_name
        self.credentials = get_credentials('soc')
        
        self.expires_in_seconds = expires_in_seconds
        
        
    def run(self, start_date: str, end_date: str) -> DataFrame:
        """_summary_

        Args:
            start_date (str): _data de início dos atestados buscados_
            end_date (str): data de fim dos atestados buscados_

        Returns:
            DataFrame: _retorna o dataframe com todos os dados dos atestados captados_
        """
        
        # self.build_func_name_request_xml()
        # return
        
        date_formatter = DateFormatter()
        start_search_date = date_formatter.months_ago(12)
        end_search_date = date_formatter.months_ahead(12)
        
        print(start_date)
        print(end_date)
        
        print(f'\nPeríodo de busca - Data início: {start_search_date} - Data fim: {end_search_date}')
        
        request_xml = self.build_request_xml(start_date=start_search_date, end_date=end_search_date)
        df: DataFrame = self.request_data(xml=request_xml)
        
        df = CompareDateFilter.is_beetween(
            df,
            column_name='dataFicha',
            start_date=date_formatter.to_datetime(start_date),
            end_date=date_formatter.to_datetime(end_date)
        )
        
        df = self.merge_funcs_infos(df=df)
        print(df)
        
        return df


    def build_request_xml(self, start_date: str, end_date: str) -> str:
        
        client_code: str
        match self.client_name:
            case 'pluri':
                client_code = '592252'
            case 'leroy':
                client_code = '560416'
            case 'viva':
                client_code = '592279'
            case _:
                raise ValueError('Erro de parametro: "client_name" é inválido, favor passar como ou "pluri", "leroy" ou "viva"')
            
        # Nonce
        nonce_raw = os.urandom(16)
        nonce_b64 = base64.b64encode(nonce_raw).decode('utf-8')

        # Timestamps UTC
        # brasilia = ZoneInfo("America/Sao_Paulo")
        now = datetime.datetime.utcnow().replace(microsecond=0)

        # now = datetime.datetime.utcnow().replace(microsecond=0)
        created = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        expires = (now + datetime.timedelta(seconds=self.expires_in_seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # PasswordDigest = SHA1(nonce + created + password)
        digest_input = nonce_raw + created.encode('utf-8') + self.credentials['pw'].encode('utf-8')
        password_digest = base64.b64encode(hashlib.sha1(digest_input).digest()).decode('utf-8')

        # Monta XML
        xml = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:ser="http://services.soc.age.com/">
            <soapenv:Header>
                <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
                                            xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
                    <wsu:Timestamp wsu:Id="TS-{(uuid.uuid4().hex).upper()}">
                        <wsu:Created>{created}</wsu:Created>
                        <wsu:Expires>{expires}</wsu:Expires>
                    </wsu:Timestamp>
                    <wsse:UsernameToken wsu:Id="UsernameToken-{(uuid.uuid4().hex).upper()}">
                        <wsse:Username>U{self.credentials['user_code']}</wsse:Username>
                        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">{password_digest}</wsse:Password>
                        <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">{nonce_b64}</wsse:Nonce>
                        <wsu:Created>{created}</wsu:Created>
                    </wsse:UsernameToken>
                </wsse:Security>
            </soapenv:Header>
            <soapenv:Body>
                <ser:consultarLoteLicencasMedicas>
                    <consultaAfastamento>
                        <codigoEmpresaFuncionario>{client_code}</codigoEmpresaFuncionario>
                        <dataInicioAfastamento>{start_date}</dataInicioAfastamento>
                        <dataFimAfastamento>{end_date}</dataFimAfastamento>
                        <dataFicha>06/09/2026</dataFicha>
                        <identificacaoVo>
                            <chaveAcesso>{self.credentials['access_key']}</chaveAcesso>
                            <codigoEmpresaPrincipal>{self.credentials['expert_code']}</codigoEmpresaPrincipal>
                            <codigoResponsavel>{self.credentials['responsible_code']}</codigoResponsavel>
                            <codigoUsuario>U{self.credentials['user_code']}</codigoUsuario>
                        </identificacaoVo>
                        <tipoAfastamento>TODOS</tipoAfastamento>
                    </consultaAfastamento>
                </ser:consultarLoteLicencasMedicas>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        return xml
    
    
    def func_name_request(self, cpf: str, client_name: str) -> DataFrame:
        """_pega o nome do funcionário por meio do exporta dados_

        Args:
            cpf (str): _cpf do funcionário_. 
            client_name (str): _nome da empresa que o funcionário trabalha_. 

        Returns:
            str: _retorna o nome do funcionário da empresa com o cpf correspondente ao passado_
        """
        all_clients_cod = {
            "leroy": "560416",
            "pluri": "592252",
            'viva': '592279'
        }
        
        client_cod = all_clients_cod[client_name]
        
        params_str: str = f'"empresa":"388105","codigo":"185170","chave":"24920146325a31c7fa94","tipoSaida":"json","empresaTrabalho":"{client_cod}","cpf":"{cpf}","parametroData":"","dataInicio":"","dataFim":""'
        req_url = f'https://ws1.soc.com.br/WebSoc/exportadados?parametro={{{params_str}}}'
        
        res = req.get(url=req_url)
        json = res.json()
        df = DataFrame(json)

        df.rename(columns={
            'NOME': 'nomeFuncionario',
            'CPFFUNCIONARIO': 'cpfFuncionario'
        }, inplace=True)
        
        df['cpfFuncionario'] = df['cpfFuncionario'].astype(str)
        
        return df.loc[0, ['nomeFuncionario', 'cpfFuncionario']].to_frame().T        
        
        
    def merge_funcs_infos(self, df: DataFrame) -> DataFrame:
        
        df['cpfFuncionario'] = df['cpfFuncionario'].astype(str)
        
        nomes = {}
        for i, cpf in enumerate(df['cpfFuncionario']):
            func_df = self.func_name_request(cpf=cpf, client_name=self.client_name)
            print(f'{i + 1}: {func_df['nomeFuncionario'][0]} - {func_df['cpfFuncionario'][0]}')
            if func_df is not None and not func_df.empty:
                nomes[cpf] = func_df.loc[0, 'nomeFuncionario']

        df['nomeFuncionario'] = df['cpfFuncionario'].map(nomes)
                
        return df
        
        

    
    # def build_func_name_request_xml(self, cpf: str = None) -> str:
        
    #     # Nonce
    #     nonce_raw = os.urandom(16)
    #     nonce_b64 = base64.b64encode(nonce_raw).decode('utf-8')

    #     # Timestamps UTC
    #     # brasilia = ZoneInfo("America/Sao_Paulo")
    #     now = datetime.datetime.utcnow().replace(microsecond=0)

    #     # now = datetime.datetime.utcnow().replace(microsecond=0)
    #     created = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    #     expires = (now + datetime.timedelta(seconds=self.expires_in_seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')

    #     # PasswordDigest = SHA1(nonce + created + password)
    #     digest_input = nonce_raw + created.encode('utf-8') + self.credentials['pw'].encode('utf-8')
    #     password_digest = base64.b64encode(hashlib.sha1(digest_input).digest()).decode('utf-8')

    #     # Monta XML
    #     xml = f"""
    #     <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    #             xmlns:ser="http://services.soc.age.com/">
    #         <soapenv:Header>
    #             <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    #                                         xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
    #                 <wsu:Timestamp wsu:Id="TS-{(uuid.uuid4().hex).upper()}">
    #                     <wsu:Created>{created}</wsu:Created>
    #                     <wsu:Expires>{expires}</wsu:Expires>
    #                 </wsu:Timestamp>
    #                 <wsse:UsernameToken wsu:Id="UsernameToken-{(uuid.uuid4().hex).upper()}">
    #                     <wsse:Username>U{self.credentials['user_code']}</wsse:Username>
    #                     <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">{password_digest}</wsse:Password>
    #                     <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">{nonce_b64}</wsse:Nonce>
    #                     <wsu:Created>{created}</wsu:Created>
    #                 </wsse:UsernameToken>
    #             </wsse:Security>
    #         </soapenv:Header>
    #         <soapenv:Body>
    #             <ser:importacaoFuncionario>
    #                 <Funcionario>
    #                     <funcionarioWsVo>
    #                         <chaveProcuraFuncionario>CPF_ATIVO</chaveProcuraFuncionario>
    #                         <situacao>ATIVO</situacao>
    #                         <cpf>13665903688</cpf>
    #                     </funcionarioWsVo>
    #                     <tipoAfastamento>TODOS</tipoAfastamento>
    #                 </Funcionario>
    #             </ser:importacaoFuncionario>
    #         </soapenv:Body>
    #     </soapenv:Envelope>
    #     """
    #     print(xml)
    #     return
    #     return xml
    

    def request_data(self, xml: str) -> DataFrame:
        
        url = "https://ws1.soc.com.br/WSSoc/services/LicencaMedicaWs"
        headers = {
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "" 
        }
        
        res = req.post(url=url, data=xml, headers=headers)
        df = pd.read_xml(res.content,  xpath=".//Afastamento")
        
        return df
    
    
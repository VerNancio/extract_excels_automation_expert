import datetime as dt

from ...helpers.tools.date_formatter import DateFormatter
from ...helpers.tools.get_credentials import get_credentials



class MakeSocRequests:
    

    @staticmethod
    def make_pluri_request(start_date: str | None, end_date: str | None) -> dict[str, str]:

        date_formatter = DateFormatter(date_format='%Y-%m-%d')

        start_date = date_formatter.format_date(start_date) if start_date is not None else date_formatter.today()
        end_date = date_formatter.format_date(end_date) if end_date is not None else date_formatter.months_ahead(months=1)


        params: str = f'"empresa":"388105","codigo":"207673","chave":"edb0300b0ad29e39b6b4","tipoSaida":"csv","empresaTrabalho":"592252","dataInicio":"{start_date}","dataFim":"{end_date}"'

        return {
            'url': f'https://ws1.soc.com.br/WebSoc/exportadados?parametro={{{params}}}',
            'params': '',
            'cookies': ''
        }
    
    
    @staticmethod
    def make_leroy_request(start_date: str | None, end_date: str | None) -> dict[str, str]:

        date_formatter = DateFormatter(date_format='%Y-%m-%d')

        start_date = date_formatter.format_date(start_date) if start_date is not None else date_formatter.today()
        end_date = date_formatter.format_date(end_date) if end_date is not None else date_formatter.months_ahead(months=1)


        params: str = f'"empresa":"559244","codigo":"207809","chave":"70015e7cc0b729e0a598","tipoSaida":"csv","empresaTrabalho":"560416","dataInicio":"{start_date}","dataFim":"{end_date}"'

        return {
            'url': f'https://ws1.soc.com.br/WebSoc/exportadados?parametro={{{params}}}',
            'params': '',
            'cookies': ''
        }
    


    def build_request_xml():

        xml = """
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
            <ns2:consultarLicencaMedicaResponse xmlns:ns2="http://services.soc.age.com/">
            <AfastamentoRetorno>
            <abonado></ abonado>
            < acidenteTrajeto></ acidenteTrajeto>
            < avisos></ avisos>
            < cidContestado></ cidContestado>
            <cids></cids>
            <codigoEmpresaFuncionario>?</codigoEmpresaFuncionario>
            <codigoFuncionario></codigoFuncionario>
            <codigoMotivoAfastamento></codigoMotivoAfastamento>
            <codigoPessoaSolicitante></codigoPessoaSolicitante>
            <codigoSequencialLicenca>?</codigoSequencialLicenca>
            <conselhoClasse></conselhoClasse>
            <cpfFuncionario></cpfFuncionario>
            <dataFicha>?</dataFicha>
            <dataFimAfastamento>?</dataFimAfastamento>
            <dataInicioAfastamento>?</dataInicioAfastamento>
            <dataSolicitacao></dataSolicitacao>
            <descricaoMotivo></descricaoMotivo>

              """



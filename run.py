import sys
import time

from src.main import main




if __name__ == '__main__':
    
    start_time = time.time()

    keys = [
        'client_name', 'date_to_filter', 'date_to_save', 'save_with_date_in_name', 
        'start_date', 'end_date', 'should_store_where', 'report_type'
    ]

    help_msg = "KWarg deve ser passado no formato para cada item desta forma: \n" \
                    "--client_name:<nome da empresa>\n" \
                    "--date_to_filter:<data pra filtrar: dd/mm/YYYY>\n" \
                    "--date_to_save:<hoje/ontem/ultimo_dia_util/ultimo_dia_ultimo_mes>\n" \
                    "--start_date:<data pra filtrar: dd/mm/YYYY>\n" \
                    "--end_date:<data pra filtrar: dd/mm/YYYY>\n" \
                    "--should_store_where:<local/onedrive/both>\n" \
                    "--report_type:<'hour'/'date'>\n" 

    kwargs = sys.argv[1:]

    if any(help_arg in kwarg for help_arg in ['-h', '--h', '-help', '--help'] for kwarg in kwargs):
        print(help_msg)
        
    else:

        kwargs_from_cmd = {}
        for arg in kwargs:
            if ':' in arg:
                key_not_striped, value = arg.split(':', 1)
                key = key_not_striped.lstrip('--')

                kwargs_from_cmd[key] = value

                if key not in keys:
                    err_msg: str = f"Chave enviada não é válida: {key}"
                    raise ValueError(err_msg)
                
            else:
                raise ValueError(help_msg)
            
        if 'client_name' not in kwargs_from_cmd:
            raise Exception('Kwarg obrigatório "client_name" não foi enviado ou está com escrita incorreta.')
            
        main(**kwargs_from_cmd)
        
    end_time = time.time()

    print('\nExecução finalizada.')
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")

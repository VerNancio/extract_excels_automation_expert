import subprocess

for type in ['hour', 'date']:
    commands = [
        f'python .\\run.py --client_name:merck --start_date:01/02/2026 --end_date:28/02/2026 --date_to_save:01/02/2026 --report_type:{type}',
        f'python .\\run.py --client_name:merck --start_date:01/03/2026 --end_date:31/03/2026 --date_to_save:01/03/2026 --report_type:{type}',
        f'python .\\run.py --client_name:merck --start_date:01/04/2026 --end_date:30/04/2026 --date_to_save:01/04/2026 --report_type:{type}',
    ]

    for cmd in commands:
        subprocess.run(cmd, shell=True)
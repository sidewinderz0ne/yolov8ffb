import subprocess

# List of script files to run
scripts_to_run = ['create_db.py', 'create_table_auth.py', 'create_table_cctv.py',
'create_table_config.py','create_table_quality.py','create_table_master_quality.py',
'create_table_bunit.py','create_table_div.py','create_table_blok.py','create_table_wb.py',]

# Loop through the list and run each script
for script in scripts_to_run:
    try:
        subprocess.run(['python', script], check=True)
        print(f'Successfully executed {script}')
    except subprocess.CalledProcessError as e:
        print(f'Error executing {script}: {e}')
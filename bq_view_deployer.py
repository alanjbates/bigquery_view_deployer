# BigQuery View Deployer with source control and continuous deployment

import subprocess
import datetime
import glob
import sys
import os

#install package on ephemeral deployment machine
subprocess.call([sys.executable, "-m", "pip", "install", "google-cloud-bigquery"])
from google.cloud import bigquery

#initialize BQ client
client = bigquery.Client()

#Set run project variable (This is set in your .yaml file)
run_project_id = os.environ['PROJECT']
print('Project: ' + run_project_id)

#set deployment dttm variable
deployment_dttm = datetime.datetime.now()

#Get a list of all files in the working directory and subfolders
files = glob.glob('*/*',recursive=True)

#Loop through each file in the list
for sql_file in files:
    #Only Examine .sql files
    if sql_file.endswith('.sql'):
        #get dataset name and view name from filename
        dataset_name = sql_file.split('.')[0]
        #if sql file is in a subfolder, drop the foldername
        if '/' in dataset_name:
            dataset_name = dataset_name.split('/')[0]
        #take the viewname from the filename
        view_name = sql_file.split('.')[1]
        print('Dataset: ' + dataset_name)
        print('View: ' + view_name)

        #get sql string
        sql_string = open(sql_file, 'r').read()

        #update sql string with _RUN_PROJECT_ID
        sql_string = sql_string.replace('_RUN_PROJECT_ID', run_project_id)
        #update sql string with _DEPLOYMENT_DTTM
        sql_string = sql_string.replace('_DEPLOYMENT_DTTM', str(deployment_dttm))

        #set BQ client params
        source_dataset_id = ''
        source_table_id = ''
        shared_dataset_ref = client.dataset(dataset_name)
        view_ref = shared_dataset_ref.table(view_name)
        view = bigquery.Table(view_ref)
        sql_template = (sql_string)
        view.view_query = sql_template.format(run_project_id, source_dataset_id, source_table_id)

        #Create/Replace View
        try:
            view = client.update_table(view, ["view_query"])
            print('REPLACED VIEW: ' + dataset_name + '.' + view_name)
        except:
            view = client.create_table(view, ["view_query"])
            print('CREATED VIEW: ' + dataset_name + '.' + view_name)

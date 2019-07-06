# BigQuery View Deployer with source control and continuous deployment

This is a simple process I created to deploy database sql views to Google BigQuery with the benefits of source control and the speed of continuous deployment.

TLDR; Hook up a Google Cloud Build trigger to your code repository of choice, In your cloudbuild.yaml file use the python 3.7 docker image and have it execute the bq_view_deployer.py script.  It will iterate through all .sql files in the repo and create/replace views in BigQuery.

![Image of Architecture](https://raw.githubusercontent.com/alanjbates/bigquery_view_deployer/master/BigQuery_View_Deployer.png)


Cloud Build Trigger
Source code is here: 
Cloud Build trigger is here: 
When a commit is merged to branch, cloud build creates a python docker image and runs a .py script which creates/replaces the sql views in the repository.
master = gcp-project-id-dev
qa = gcp-project-id-qa
prod = gcp-project-id-prod

bq_view_deployer.py
This script loops through each sql file in the repo
It replaces dynamic variables in the .sql file text:
_RUN_PROJECT_ID with the current project id eg: gcp-project-id-prod
_DEPLOYMENT_DTTM is replaced with now() eg: 2019-07-01 21:25:56.516117
It gets the BigQuery dataset and view name from the .sql filename
for example take filename:  'weather_data.my_weather_aggregate.sql' 
dataset_name is the string before the first '.' eg: 'weather_data'
view_name is the middle string eg: 'my_weather_aggregate'
For each .sql in the repo, it will create or replace the view automatically.

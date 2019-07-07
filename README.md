# BigQuery View Deployer with source control and continuous deployment

This is a simple process I created to deploy and maintain database sql views to Google BigQuery with the benefits of source control and the speed of continuous deployment.

#### TLDR; 
Hook up a Google Cloud Build trigger to your code repository of choice. In your cloudbuild.yaml file use the python 3.7 docker image and have it execute the bq_view_deployer.py script.  It will iterate through all .sql files in the repo and create/replace/drop views in BigQuery.

![Image of Architecture](https://raw.githubusercontent.com/alanjbates/bigquery_view_deployer/master/BigQuery_View_Deployer.png)


### Cloud Build Trigger

Use the GCP UI to create a new Cloud Build Trigger.  Choose your repo and tie to a specific branch.  Have it use the Cloud Build configuration file method and point it to the bq_view_deployer.yaml file.

When a commit is merged to branch, cloud build creates a python docker image and runs a .py script which creates/replaces the sql views in the repository.

Your GCP project cloud build service account needs to have the BigQuery Admin IAM role: _yourGCPprojectnumber_@cloudbuild.gserviceaccount.com

When you create the triggers in each environment you can tie a specific branch to each project's trigger to manage.

master branch = gcp-project-id-dev

qa branch = gcp-project-id-qa

prod branch = gcp-project-id-prod

### Python Script
 
The bq_view_deployer.py script loops through each .sql file in the repo and will create/repalce them in BigQuery.

It replaces dynamic variables in the .sql file text:
* _RUN_PROJECT_ID with the current project id eg: gcp-project-id-prod
* _DEPLOYMENT_DTTM is replaced with now() eg: 2019-07-01 21:25:56.516117

It gets the BigQuery dataset and view name from the .sql filename
for example take filename:  'weather_data.my_weather_aggregate.sql' 
* dataset_name is the string before the first '.' eg: 'weather_data'
* view_name is the middle string eg: 'my_weather_aggregate'

### SQL files



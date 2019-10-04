# BigQuery View Deployer

import subprocess
import datetime
import glob
import sys
import os
import git
from google.cloud import bigquery

#initialize BQ client
client = bigquery.Client()

#Set run project variable
run_project_id = os.environ['PROJECT']
print('Project: ' + run_project_id)

#set branch variable based on the project ID if you have a different project for dev/qa/prod
if run_project_id == 'YOUR DEV PROJECT NAME':
    git_branch = 'origin/master'
elif run_project_id == 'YOUR QA PROJECT NAME':
    git_branch = 'origin/qa'
elif run_project_id == 'YOUR PROD PROJECT NAME':
    git_branch = 'origin/prod'

#set deployment dttm variable
deployment_dttm = datetime.datetime.now()

## Module Constants
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
commit_hash   = os.environ['COMMIT_SHA']
path = './YOURCLOUDSOURCEREPOSITORYNAME/'


#Create git examination functions
# major kudos to this guy for the functions --> https://bbengfort.github.io/snippets/2016/05/06/git-diff-extract.html
def versions(path, branch=git_branch):
    """
    This function returns a generator which iterates through all commits of
    the repository located in the given path for the given branch. It yields
    file diff information to show a timeseries of file changes.
    """

    # Create the repository, raises an error if it isn't one.
    repo = git.Repo(path)

    # Iterate through every commit for the given branch in the repository
    for commit in repo.iter_commits(branch):
        # Determine the parent of the commit to diff against.
        # If no parent, this is the first commit, so use empty tree.
        # Then create a mapping of path to diff for each file changed.
        parent = commit.parents[0] if commit.parents else commit_hash
        diffs  = {
            diff.a_path: diff for diff in commit.diff(parent)
        }

        # The stats on the commit is a summary of all the changes for this
        # commit, we'll iterate through it to get the information we need.
        for objpath, stats in commit.stats.files.items():

            # Select the diff for the path in the stats
            diff = diffs.get(objpath)

            # If the path is not in the dictionary, it's because it was
            # renamed, so search through the b_paths for the current name.
            if not diff:
                for diff in diffs.values():
                    if diff.b_path == path and diff.renamed:
                        break

            # Update the stats with the additional information
            stats.update({
                'object': os.path.join(path, objpath),
                'commit': commit.hexsha,
                'author': commit.author.email,
                'timestamp': commit.authored_datetime.strftime(DATE_TIME_FORMAT),
                'size': diff_size(diff),
                'type': diff_type(diff),
            })

            yield stats


def diff_size(diff):
    """
    Computes the size of the diff by comparing the size of the blobs.
    """
    if diff.b_blob is None and diff.deleted_file:
        # This is a deletion, so return negative the size of the original.
        return diff.a_blob.size * -1

    if diff.a_blob is None and diff.new_file:
        # This is a new file, so return the size of the new value.
        return diff.b_blob.size

    # Otherwise just return the size a-b
    return diff.a_blob.size - diff.b_blob.size


def diff_type(diff):
    """
    Determines the type of the diff by looking at the diff flags.
    """
    if diff.renamed: return 'RENAMED'
    if diff.deleted_file: return 'ADDED'
    if diff.new_file: return 'DELETED'
    return 'MODIFIED'

#Call the git tree examination functions
git_activity = versions(path)

#Create empty list to store the names of the new/changed files
views_to_deploy = []

#Get the new/changed file names
for record in git_activity:
    if record['commit'] == commit_hash \
            and record['type'] != 'DELETED'\
            and str(record['object']).endswith('.sql'):
        views_to_deploy.append(record['object'])

print('IDENTIFIED ', len(views_to_deploy), ' NEW/CHANGED SQL FILES IN THE COMMIT.')

#Loop through each sql file in the list and take action
for sql_file in views_to_deploy:

    #slice the filename from the full path string
    name_string = sql_file.split('/')[2]

    #get dataset name and view name from filename
    dataset_name = name_string.split('.')[0]

    #if sql file is in a subfolder, drop the foldername
    if '/' in dataset_name:
        dataset_name = dataset_name.split('/')[0]

    #take the viewname from the filename
    view_name = str(sql_file.split('.')[2])
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
        print('Not able to REPLACE view, attempting CREATE')
        pass

    try:
        view = client.create_table(view, ["view_query"])
        print('CREATED VIEW: ' + dataset_name + '.' + view_name)
    except:
        print('Not able to CREATE view, SKIPPING ' + dataset_name + '.' + view_name)
        pass

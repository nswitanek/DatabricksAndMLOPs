import os

import requests

def get_pipeline_id(release_name, organization, project, personal_access_token):
    release_found = (-1, "Default message") # Default to no available release

    url = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines?api-version=6.0-preview.1"

    username = "accessToken"
    password = personal_access_token

    results = requests.get(url, auth=(username, password))

    if results.status_code == 200:
        try:
            data = results.json()
            
            if data["count"] == 0:
                release_found = (-1, "There are no release definitions found.")
            else:
                candidate_releases = [r["id"] for r in data["value"] if r["name"] == release_name]
                if len(candidate_releases) > 0:
                    release_found = (candidate_releases[0], release_name)
                else:
                    release_found = (
                        -1, 
                        "There was no release definition found with the name '{}'".format(release_name)
                    )

        except Exception as e:
            release_found = (-1, e.message)
        
    else:
        release_found = (-1, results.content)
    
    return release_found
    

def execute_pipeline(pipeline_id, organization, project, personal_access_token, azdo_variables=None):
    
    url = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0-preview.1"

    username = "accessToken"
    password = personal_access_token

    data = {"variables":{}}
    if azdo_variables:
        # Must be in the form
        # "variables":{"my_variable_name":{"value":"anewvalue", "isSeret":bool}}
        data.update({"variables":azdo_variables})

    header = {"Content-Type":"application/json"}

    results = requests.post(url, auth=(username, password), json=data, headers=header)

    output = dict()
    if results.status_code == 200:
        results_json = results.json()
        output["new_pipeline_id"] = results_json.get("id", "NotAssigned")
        output["new_pipeline_name"] = results_json.get("name", "NotAssigned")
        output["new_pipeline_url"] = results_json.get("url", "NotAssigned")
    else:
        output["error"] = results.json()["message"]
    
    return output


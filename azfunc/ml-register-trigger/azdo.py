import os

import requests

def get_release_id(release_name):
    release_found = (-1, "Default message") # Default to no available release

    url = "https://vsrm.dev.azure.com/{organization}/{project}/_apis/release/definitions?api-version=5.1".format(
        organization = os.environ.get("devops_organization"),
        project = os.environ.get("devops_project")
    )

    username = os.environ.get("personal_access_token")
    password = os.environ.get("personal_access_token")

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
    

def execute_release(release_id, azdo_variables=None):
    
    url = "https://vsrm.dev.azure.com/{organization}/{project}/_apis/release/releases?api-version=5.1".format(
        organization = os.environ.get("devops_organization"),
        project = os.environ.get("devops_project")
    )

    username = os.environ.get("personal_access_token")
    password = os.environ.get("personal_access_token")

    data = {
        "definitionId": release_id,
        "description": "Creating Sample release",
        "isDraft": False,
        "reason": "none"
    }
    if azdo_variables:
        # Must be in the form
        # "variables":{"my_variable_name":{"value":"anewvalue"}}
        data.update({"variables":azdo_variables})

    header = {"Content-Type":"application/json"}

    results = requests.post(url, auth=(username, password), json=data, headers=header)

    output = dict()
    if results.status_code == 200:
        output["new_release_id"] = results.json()["id"]
        output["new_release_name"] = results.json()["name"]
        output["new_release_status"] = results.json()["status"]
    else:
        output["error"] = results.json()["message"]
    
    return output


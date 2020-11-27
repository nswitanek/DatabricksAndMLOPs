import os

import requests
from azure.common.credentials import get_azure_cli_credentials
resource_group = os.environ.get("DBR_RESOURCE_GROUP")
databricks_workspace = os.environ.get("DBR_WORKSPACE_NAME")
dbricks_location = os.environ.get("LOCATION")

credentials, subscription_id = get_azure_cli_credentials()
dbricks_api = f"https://{dbricks_location}.azuredatabricks.net/api/2.0"
# Get a token for the global Databricks application. This value is fixed and never changes.
adbToken = credentials.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d").token
# Get a token for the Azure management API
azToken = credentials.get_token("https://management.core.windows.net/").token
dbricks_auth = {
    "Authorization": f"Bearer {adbToken}",
    "X-Databricks-Azure-SP-Management-Token": azToken,
    "X-Databricks-Azure-Workspace-Resource-Id": (
        f"/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Databricks"
        f"/workspaces/{databricks_workspace}")}
results = requests.post(f"{dbricks_api}/token/create", headers= dbricks_auth).json()

print(results)
print(results["token_value"])
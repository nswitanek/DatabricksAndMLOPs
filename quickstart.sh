RG_NAME=demotest01
SECRET_SCOPE_NAME=demoscope

echo "###Beginning Resource Group Creation"
az group create -l eastus2 -g $RG_NAME
echo "###Beginning Resource Group Deployment"
az deployment group create -g $RG_NAME -f ./setup/ml-arm-template.json -p @./setup/ml-arm-template-parameters.json

echo "Collect PAT from Databricks: https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/authentication"
echo "Configure your CLI: https://docs.microsoft.com/en-us/azure/databricks/dev-tools/cli/"
read  -n 1 -p "Press Enter when you've completed Databricks CLI configuration..."

# Create a Secret Scope
databricks secrets create-scope --scope $SECRET_SCOPE_NAME --initial-manage-principal users

# Set a Secret
databricks secrets put --scope $SECRET_SCOPE_NAME --key amlstoragekey --string-value $STORAGE_KEY




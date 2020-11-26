#!/bin/bash

RG_NAME=demotest01
SECRET_SCOPE_NAME=demoscope
STORAGE_ACCOUNT_NAME=saihh6ecvjpjxhw
DEPLOYMENT_NAME=aml-dbr-deployment

echo "###Beginning Resource Group Creation"
az group create -l eastus2 -g $RG_NAME
echo "###Beginning Resource Group Deployment"
az deployment group create -g $RG_NAME -n $DEPLOYMENT_NAME -f ./setup/infra-arm-template.json -p @./setup/infra-arm-template-parameters.json --parameters storageAccountName=$STORAGE_ACCOUNT_NAME

end=$(date -u -d "30 minutes" '+%Y-%m-%dT%H:%MZ')
ARM_OUTPUTS=$(az deployment group show --name $DEPLOYMENT_NAME --resource-group $RG_NAME --query properties.outputs)
STORAGE_KEY=$(echo $ARM_OUTPUTS | jq '.storageAccountKey.value')
AML_WORKSPACE_NAME=$(echo $ARM_OUTPUTS | jq '.amlWorkspace.value' | tr -d '\"')
TRAIN_SAS_TOKEN=$(az storage blob generate-sas -n training.csv --account-name $STORAGE_ACCOUNT_NAME --account-key $STORAGE_KEY --container-name data --permissions arw --expiry $end | tr -d '\"')
VALIDATE_SAS_TOKEN=$(az storage blob generate-sas -n validation.csv --account-name $STORAGE_ACCOUNT_NAME --account-key $STORAGE_KEY --container-name data --permissions arw --expiry $end | tr -d '\"')

echo "Collect PAT from Databricks: https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/authentication"
echo "Configure your CLI: https://docs.microsoft.com/en-us/azure/databricks/dev-tools/cli/"
read  -n 1 -p "Press Enter when you've completed Databricks CLI configuration..."

# Create a Secret Scope
echo "Creating a Secret Scope and Secret Value"
databricks secrets create-scope --scope $SECRET_SCOPE_NAME --initial-manage-principal users

# Set a Secret
databricks secrets put --scope $SECRET_SCOPE_NAME --key amlstoragekey --string-value $STORAGE_KEY

# # Generate Training Data
echo "Beginning generation of training and validation data"
python3 setup/generate_data.py

# Copy training and validation
echo "Beginning transfer of data to Storage Account '$STORAGE_ACCOUNT_NAME'"
azcopy cp ./data/training.csv "https://$STORAGE_ACCOUNT_NAME.blob.core.windows.net/data/training.csv?$TRAIN_SAS_TOKEN"
azcopy cp ./data/validation.csv "https://$STORAGE_ACCOUNT_NAME.blob.core.windows.net/data/validation.csv?$VALIDATE_SAS_TOKEN"

echo "AZURE ML: Attaching the new container as a datastore for $AML_WORKSPACE_NAME"
echo "Running: az ml datastore attach-blob --account-name $STORAGE_ACCOUNT_NAME --container-name data --name datacontainer --workspace-name $AML_WORKSPACE_NAME --resource-group $RG_NAME"
az ml datastore attach-blob --account-name $STORAGE_ACCOUNT_NAME --container-name data --name datacontainer --workspace-name $AML_WORKSPACE_NAME --resource-group $RG_NAME

echo "AZURE ML: Registering the uploaded datasets"
az ml dataset register -f data/aml-training-dataset.json --workspace-name $AML_WORKSPACE_NAME --resource-group $RG_NAME --skip-validation
az ml dataset register -f data/aml-validation-dataset.json --workspace-name $AML_WORKSPACE_NAME --resource-group $RG_NAME --skip-validation


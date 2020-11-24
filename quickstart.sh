as group create -l eastus2 -g demotest01
az deployment group create -g demotest01 -f arm-template.json -p @arm-template-parameters.json

az devops project create --name databricksamldevops --org "" --description "A demo of using Azure Databricks and Azure ML DevOps"


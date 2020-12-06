# DatabricksAndMLOPs
Demonstrating Azure ML and Azure Databricks DevOps Patterns.

This repository demonstrates the following activities:

* Databricks
  * Run unit tests
  * Upload notebooks
* Azure ML
  * Create and publish an ml pipeline
  * Automatically register a model if it beats that latest model's performance.
  * Pytest functions
  * Trigger pipeline run (no wait)
  * On Model Registration, deploy to ACI
* Azure Function
  * Azure App Configuration integration (optional)
  * Waiting for a model registration event
  * Trigger an Azure DevOps Release pipeline

## Quickstart

* Create an [Azure DevOps project](https://docs.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops&tabs=preview-page).
* Install the [Azure Databricks Extension in Azure DevOps](https://marketplace.visualstudio.com/items?itemName=riserrad.azdo-databricks).
* Create two [Azure Service Connections](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops) 
  * One with subscription level scope named `rg-arm-service-connection`.
  * One with an Azure Machine Learning Workspace scope named `aml-service-connection`.
* Create a [Azure AD Service Principal](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal).
* Create a [Variable Group](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=yaml) named `AMLDBRVariables`.
  * Populate the variable group with the following variables
  ```
  AML_RESOURCE_GROUP mlopsdemo <Your Resource Group Name>
  LOCATION eastus2 <The Location of your resource group>
  TENANT_ID <The Azure Active Directory Tenant Id>
  AML_SUBSCRIPTION_ID <Your Subscription ID>
  AML_WORKSPACE_NAME <Your Desired Workspace Name (must be unique)>
  CLIENT_ID <Your service principals Client Id>
  CLIENT_SECRET <Your service principals Client Secret>
  DBR_RESOURCE_GROUP mlopsdemo <Resource Group name that hold the Databricks Workspace>
  DBR_COMPUTE_NAME adbcompute<Your Databricks Compute Name>
  DBR_WORKSPACE_NAME adbrmlopsdemo <The name of the Databricks Workspace>
  ```
* Create the following [Release Pipelines](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/?view=azure-devops) from the existing YAML files.
  * "SetupInfrastructure" from `devops/setup-devops-pipeline.yaml`.
    * Update the parameters in `setup/infra-arm-template-parameters.json` .
    * Make special note of `azDOOrganization` and `azDOProject`.
    * Execute the pipeline.
  * "DeployMLOpsFunc" from `devops/func-devops-pipeline.yaml` and execute it.
  * "DeployNotebooks" from `devops/dbr-devops-pipeline.yaml` and execute it.
  * "DeployRegisteredModel" from `devops/deploy-registered-model.yaml`. Do not execute it.
  * "DeployMLPipelineAndTrain" from `devops/ml-pipeline-endpoint-pipeline.yaml`.

## How Do Different Roles Use This Repo?

### Azure Machine Learning MLOps

* Data Scientists Checks in Code to Run Experiment
* A Model is Trained and Validated Against Validation Set and Existing Metrics
* A Model is Registered and Must be Deployed to Test Environment

### Azure Databricks 

* Data Scientist or Engineer Wants to Build Unit Tests for their Notebooks
* Data Scientist or Engineer Wants to Validate Job Scheduling JSON

# References

* Azure ML and Azure ML Pipelines
  * [What are Azure ML Pipelines?](https://docs.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines)
* Deploy and Serve Model from Azure Databricks onto Azure Machine Learning
  * [Talk](https://databricks.com/session_na20/deploy-and-serve-model-from-azure-databricks-onto-azure-machine-learning)
  * [Slides](https://www.slideshare.net/databricks/deploy-and-serve-model-from-azure-databricks-onto-azure-machine-learning)
  * [Azure Databricks as Compute Target(Github Tutorial)](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-use-databricks-as-compute-target.ipynb)
  * [Deploy PySpark Model on AML(Github Tutorial)](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/deployment/spark/model-register-and-deploy-spark.ipynb)
  * [Inference Config JSON Schema](https://docs.microsoft.com/en-us/azure/machine-learning/reference-azure-machine-learning-cli#inference-configuration-schema)
* Azure Machine Learning Event Grid Integration
  * [Tutorial](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid)
  * [Schema Docs](https://docs.microsoft.com/en-us/azure/event-grid/event-schema-machine-learning)
  * [Additional Sample on Github](https://github.com/Azure-Samples/MachineLearningSamples-NoCodeDeploymentTriggeredByEventGrid)
* Azure DevOps
  * [What are Azure Pipelines?](https://docs.microsoft.com/en-us/azure/devops/pipelines/get-started/pipelines-get-started?view=azure-devops)
  * [Create a Personal Access Token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page)
  * [Pipeline YAML Schema Reference](https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema?view=azure-devops&tabs=schema%2Cparameter-schema)
  * [Create Releases REST API](https://docs.microsoft.com/en-us/rest/api/azure/devops/release/releases/create?view=azure-devops-rest-6.0)
* Azure Functions
  * [Developer Reference](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
  * [VS Code Extension](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp).
* Azure Databricks Authentication
  * [Using AAD to reach Databricks REST Endpoints](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/aad/service-prin-aad-token).
  * [The Tokens API](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/tokens).
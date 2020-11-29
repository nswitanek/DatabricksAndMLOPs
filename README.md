# DatabricksAndMLOPs
Demonstrating Azure ML and Azure Databricks DevOps Patterns

## Setup

* Install the [Azure Databricks Extension in Azure DevOps](https://marketplace.visualstudio.com/items?itemName=riserrad.azdo-databricks).

### Azure Machine Learning MLOps

* Data Scientists Checks in Code to Run Experiment
* A Model is Trained and Validated Against Validation Set and Existing Metrics
* A Model is Registered and Must be Deployed to Test Environment

### Azure Databricks 

* Data Scientist or Engineer Wants to Build Unit Tests for their Notebooks
* Data Scientist or Engineer Wants to Validate Job Scheduling JSON

## DevOps walkthrough

* Setup
  * Create project
  * Create variable group
  * Create Az KV backed secret scope in Databricks (https://docs.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes#azure-key-vault-backed-scopes)
  * Create databricks access token
  * Store databricks access token in variable group
  * Store storage account secret in key vault
  * Mount storage account with a spark-submit on azure databricks cli
  * Azure ML: Create Databricks connection
  * Azure ML: Create Azure ML Pipeline and Publish
  * Azure ML/Databricks: Validation of model 
  

* Databricks
  * Run unit tests
  * Get access token (variable group)
  * Configure Databricks CLI
  * Upload notebooks

* Azure ML
  * https://pumpingco.de/blog/run-an-azure-pipelines-job-only-if-source-code-has-changed/
  * Create and publish pipeline
  * Pytest functions
  * Trigger pipeline run (no wait)
  
* Azure ML
  * On Model Registration, deploy to ACI

* Azure Function
  * Azure App Configuration integration (optional)
  * Waiting for a model registration event
  * Kick off specific pipeline

# Quickstart Prerequisites

* Azure CLI: Logged in and Default subscription set.
* Databricks CLI: Installed and Configured mid-quickstart.
* AzCopy CLI: `azcopy` installed and `azcopy login` ran.
* Azure CLI ML Extension: [Docs](https://docs.microsoft.com/en-us/azure/machine-learning/reference-azure-machine-learning-cli)

# References

* Azure ML Pipelines
  * [What are Azure ML Pipelines?](https://docs.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines)
* Deploy and Serve Model from Azure Databricks onto Azure Machine Learning
  * [Talk](https://databricks.com/session_na20/deploy-and-serve-model-from-azure-databricks-onto-azure-machine-learning)
  * [Slides](https://www.slideshare.net/databricks/deploy-and-serve-model-from-azure-databricks-onto-azure-machine-learning)
  * [Azure Databricks as Compute Target(Github Tutorial)](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-use-databricks-as-compute-target.ipynb)
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
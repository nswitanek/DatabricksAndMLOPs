import argparse
import os

from azureml.core import Model, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice, AksWebservice


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--environment-name")
    parser.add_argument("-i", "--model-id")
    parser.add_argument("-n", "--service-name")
    parser.add_argument("-s", "--scoring-script")
    args = parser.parse_args()
    
    # Authenticate to AML Workspace
    sp = ServicePrincipalAuthentication(
        tenant_id=os.environ.get("TENANT_ID"),
        service_principal_id=os.environ.get("CLIENT_ID"),
        service_principal_password=os.environ.get("CLIENT_SECRET")
    ) 

    print("Connecting to AML Workspace")
    ws = Workspace.get(
        name=os.environ.get("AML_WORKSPACE_NAME"),
        subscription_id=os.environ.get("AML_SUBSCRIPTION_ID"),
        auth=sp
    )

    env = Environment.get(ws, name='AzureML-PySpark-MmlSpark-0.15')

    inference_config = InferenceConfig(
        entry_script=args.scoring_script, 
        environment=env,
    )

    model = Model(ws, id=args.model_id)

    # These should PySpark and Spark version 2.4.5
    print(model.model_framework)
    print(model.model_framework_version)

    deployment_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=2)
    
    service = Model.deploy(ws, args.service_name, [model], inference_config, deployment_config, overwrite=True)
    try:
        service.wait_for_deployment(show_output = True)
    except Exception as e:
        print("There was a failure")
        print(service.get_logs())
        print("="*10)
        raise e
    print(service.state)
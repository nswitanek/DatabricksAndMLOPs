import argparse
import os

from azureml.core import Model, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice, AksWebservice, LocalWebservice

from azureml.core.webservice import LocalWebservice, Webservice


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--environment-name")
    parser.add_argument("-i", "--model-id")
    parser.add_argument("-n", "--service-name")
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

    env = Environment.get(ws, "AzureML-PySpark-MmlSpark-0.15").clone(args.environment_name)

    inference_config = InferenceConfig(
        entry_script='./ml/score/score.py', 
        environment=env
    )

    model = Model(ws, id=args.model_id)

    deployment_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=2)
    
    service = Model.deploy(ws, args.service_name, [model], inference_config, deployment_config)
    service.wait_for_deployment(show_output = True)
    print(service.state)
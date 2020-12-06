import argparse
import os

from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.compute import ComputeTarget, DatabricksCompute
from azureml.exceptions import ComputeTargetException

if __name__ == "__main__":
    """
    Build the pipeline that trains, validates, and conditionally registers
    the model (upon successful validation).

    Expects a service principal and other parameters for AML and Databricks
    workspaces, along with the intendend training and validation sets.
    """

    databricks_compute_name = os.environ.get("DBR_COMPUTE_NAME")
    databricks_workspace_name = os.environ.get("DBR_WORKSPACE_NAME")
    databricks_access_token = os.environ.get("DBR_ACCESS_TOKEN")
    databricks_resource_group = os.environ.get("DBR_RESOURCE_GROUP")

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
    
    # Get Compute Target
    print("Gathering Compute Target")
    try:
        databricks_compute = ComputeTarget(
            workspace=ws, name=databricks_compute_name)
        print('Compute target already exists')
    except ComputeTargetException:
        print('Compute not found. Attempting to create.')
        print('databricks_compute_name {}'.format(databricks_compute_name))
        print('databricks_workspace_name {}'.format(databricks_workspace_name))
        print('databricks_access_token {}'.format(databricks_access_token))

        # Create attach config
        attach_config = DatabricksCompute.attach_configuration(
            resource_group=databricks_resource_group,
            workspace_name=databricks_workspace_name,
            access_token=databricks_access_token
        )
        databricks_compute = ComputeTarget.attach(
            ws,
            databricks_compute_name,
            attach_config
        )

        databricks_compute.wait_for_completion(True)

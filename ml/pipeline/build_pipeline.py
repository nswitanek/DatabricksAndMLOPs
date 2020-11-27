import argparse
from datetime import datetime
import os

from azureml.core import Datastore, RunConfiguration, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.compute import ComputeTarget, DatabricksCompute
from azureml.core.databricks import PyPiLibrary
from azureml.data.data_reference import DataReference
from azureml.exceptions import ComputeTargetException
from azureml.pipeline.core import Pipeline, PipelineData, PipelineEndpoint
from azureml.pipeline.steps import DatabricksStep


if __name__ == "__main__":
    """
    Build the pipeline that trains, validates, and conditionally registers
    the model (upon successful validation).

    Expects a service principal and other parameters for AML and Databricks
    workspaces, along with the intendend training and validation sets.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--pipeline-name", 
        help="The name of the pipeline to be built or updated.")
    parser.add_argument("-s", "--datastore-name", 
        help="The name of the pipeline to be built or updated.")
    parser.add_argument("-d", "--description", 
        help="The description of the pipeline to be built or updated.")

    args = parser.parse_args()

    # TODO: Make this more dynamic
    pipeline_name = args.pipeline_name
    datastore_name = args.datastore_name
    description = args.description
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
    ws.write_config()

    # Get Compute Target
    print("Gathering Compute Target")
    try:
        databricks_compute = ComputeTarget(
            workspace=ws, name=databricks_compute_name)
        print('Compute target already exists')
    except ComputeTargetException:
        print('compute not found')
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

    # Get Datastore
    print("Getting the existing Datastore")
    def_blob_store = Datastore(ws, datastore_name)
    
    # Get Dataset for Training
    print("Creating Training and Validation data references")
    # TODO: Make this more dynamic
    training_input = DataReference(datastore=def_blob_store, path_on_datastore="training",
                                        data_reference_name="trainingcsv")
    # Get Dataset for Validation
    # TODO: Make this more dynamic
    validation_input = DataReference(datastore=def_blob_store, path_on_datastore="validation",
                                        data_reference_name="validationcsv")
    training_model_output = PipelineData("output", datastore=def_blob_store)
    
    print("Creating Pipeline Steps")
    # Create Pipeline Steps
    train = DatabricksStep(
        name = "Train Model on Databricks", 
        inputs=[training_input], outputs=[training_model_output], 
        spark_version="7.3.x-cpu-ml-scala2.12",
        node_type="Standard_DS3_v2", 
        num_workers=1,
        # TODO: Make this dynamic 
        notebook_path="/Shared/DemoApp/training", 
        notebook_params={"INPUT_PATH": "", "OUTPUT_PATH": ""}, 
        runconfig=None, 
        pypi_libraries=[PyPiLibrary("azureml-databricks")], egg_libraries=None, 
        compute_target=databricks_compute, 
        version="0.01")

    register = DatabricksStep(
        name = "Validate Model on Databricks", 
        inputs=[training_model_output, validation_input], outputs=None,
        spark_version="7.3.x-cpu-ml-scala2.12",
        node_type="Standard_DS3_v2", 
        num_workers=1,
        # TODO: Make this dynamic 
        notebook_path="/Shared/DemoApp/validation", 
        notebook_params=None, 
        runconfig=None, 
        pypi_libraries=[PyPiLibrary("azureml-databricks")], egg_libraries=None, 
        compute_target=databricks_compute, 
        version="0.01")

    # Create the pipeline and publish it
    current_date_time = datetime.strftime(datetime.now(), r'%Y%m%d%H%M')
    pipe = Pipeline(
        ws,
        steps = [train, register]
    )
    print("Publishing Pipelines")
    current_active_pipe_name = pipeline_name+current_date_time
    published_pipe = pipe.publish(current_active_pipe_name)

    print("New Published Pipeline: {}".format(str(published_pipe)))

    try:
        pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name=pipeline_name)
        pipeline_endpoint.add_default(published_pipe)
        # Disable older pipelines to keep only one active in the endpoint
        all_active_sub_pipes = pipeline_endpoint.list_pipelines()
        for active_pipe in all_active_sub_pipes:
            if active_pipe.name == current_active_pipe_name:
                continue
            print(f"INFO: Disabling child pipeline '{active_pipe.name}'")
            active_pipe.disable()

        print("Successfully Added to existing pipeline")
        
    except Exception:
        pipeline_endpoint = PipelineEndpoint.publish(
            workspace=ws,
            name=pipeline_name,
            pipeline=published_pipe,
            description=description
        )
        print("Successfully created a new pipeline endpoint.")

    print("Completed pipeline build and deployment.")


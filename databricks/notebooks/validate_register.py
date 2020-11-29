# Databricks notebook source
# MAGIC %md
# MAGIC # Validation of Home Purchase Price Analysis

# COMMAND ----------

VALIDATION_PATH = dbutils.widgets.get("validation")
MODEL_PATH = dbutils.widgets.get("model_path")
MODEL_NAME = dbutils.widgets.get("model_name")
trained_model_config = dbutils.widgets.get("model_path_blob_config")
trained_model_secret_name = dbutils.widgets.get("model_path_blob_secretname")
validation_config = dbutils.widgets.get("validation_blob_config")
validation_secret_name = dbutils.widgets.get("validation_blob_secretname")

# COMMAND ----------

import argparse
import os
import uuid

from azureml.core import Run, Model
from azureml.core.authentication import AzureMLTokenAuthentication
from azureml.core.resource_configuration import ResourceConfiguration

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.pipeline import Pipeline
from pyspark.sql.types import *


# This argument parsing is necessary for getting the Run Context
parameters = ['AZUREML_RUN_TOKEN', 'AZUREML_RUN_TOKEN_EXPIRY', 'AZUREML_RUN_ID', 'AZUREML_ARM_SUBSCRIPTION', 
              'AZUREML_ARM_RESOURCEGROUP', 'AZUREML_ARM_WORKSPACE_NAME', 'AZUREML_ARM_PROJECT_NAME', 
              'AZUREML_SERVICE_ENDPOINT' ]
for param in parameters:
  temp_value = dbutils.widgets.get(f"--{param}")
  print(f"Working on: {param} with vaule {temp_value}")
  os.environ[param] = temp_value
  print(f"Checking that it's set: {os.environ[param]}")

# os.environ["AZUREML_EXPERIMENT_ID"] = 'e6abe464-c6fd-45de-9303-539b34e66b69'

trained_model_uuid = str(uuid.uuid4())
validation_uuid = str(uuid.uuid4())
print(trained_model_uuid)
print(validation_uuid)
print(VALIDATION_PATH)
print(MODEL_PATH)

# COMMAND ----------

import json

print(json.dumps(sorted(list(dict(os.environ).keys())),indent=2))

# COMMAND ----------

run = Run.get_context(allow_offline=False)

# COMMAND ----------

ws = run.experiment.workspace
MODEL_EXISTS = True
NEW_MODEL_PERFORMS_BETTER = False
if MODEL_NAME not in ws.models:
  MODEL_EXISTS = False

# COMMAND ----------

# auth = AzureMLTokenAuthentication.create(
#   azureml_access_token=os.environ['AZUREML_RUN_TOKEN'], 
#   expiry_time=os.environ['AZUREML_RUN_TOKEN_EXPIRY'], 
#   host=os.environ['AZUREML_SERVICE_ENDPOINT'], 
#   subscription_id=os.environ['AZUREML_ARM_SUBSCRIPTION'], 
#   resource_group_name=os.environ['AZUREML_ARM_RESOURCEGROUP'], 
#   workspace_name=os.environ['AZUREML_ARM_WORKSPACE_NAME'], 
#   experiment_name="testcli", 
#   run_id= os.environ['AZUREML_RUN_ID']
# )

# print(type(auth))
# print("===")
# print(dir(auth))

# COMMAND ----------

# Temporary Path to Trained Model file
model_mount_point = f"/mnt/tmp/{trained_model_uuid}"
dbutils.fs.mount(
  source = MODEL_PATH,
  mount_point = model_mount_point,
  extra_configs = {trained_model_config:dbutils.secrets.get(scope = "amlscope", key = trained_model_secret_name)}
)

# Temporary Path to Validation data path
validation_mount_point = f"/mnt/tmp/{validation_uuid}"
dbutils.fs.mount(
  source = VALIDATION_PATH,
  mount_point = validation_mount_point,
  extra_configs = {validation_config:dbutils.secrets.get(scope = "amlscope", key = validation_secret_name)}
)

# COMMAND ----------

try:
  print(dbutils.fs.ls(MODEL_PATH))
  print(print(dbutils.fs.ls(validation_mount_point)))
  print(print(dbutils.fs.ls(model_mount_point)))
except:
  print("There was a failure here")

# COMMAND ----------

print("Validating that the model can be read in and score on new data")
schema = StructType([
  StructField('YearBuilt', StringType(), True),
  StructField('Bedrooms', IntegerType(), True),
  StructField('Bathrooms', DecimalType(), True),
  StructField('Square Footage', IntegerType(), True),
  StructField('AvgSchoolRanking', DecimalType(), True),
  StructField('LastSalePrice', DecimalType(), True)
])
validation_df = spark.read.csv(VALIDATION_PATH, header=True, schema=schema)
pipe = Pipeline.load(MODEL_PATH)
results = pipe.transform(validation_df)
# Performance Metrics
challenger_mse = RegressionEvaluator(labelCol="LastSalePrice", metricName='mse')
print(challenger_mse)

# COMMAND ----------

if MODEL_EXISTS:
  # Load previous model
  # Score
  # Compare
  NEW_MODEL_PERFOMS_BETTER = True

# COMMAND ----------

# TODO: This should really be a dynamic query to see what the current threshold is
if NEW_MODEL_PERFORMS_BETTER or not MODEL_EXISTS:
    registered_model = Model.register(
        workspace=ws,
        model_name=MODEL_NAME, # Name of the registered model in your workspace.
        model_path='/dbfs/'+MODEL_PATH, # Local file to upload and register as a model.
        resource_configuration=ResourceConfiguration(cpu=1, memory_in_gb=1),
        description='A sample model.',
        tags={'tag1': 'value1', 'tag2': 'value2'}
    )
    print(registered_model)
else:
    print("Model did not meet threshold for registration")
    print("MSE: {}".format(challenger_mse))

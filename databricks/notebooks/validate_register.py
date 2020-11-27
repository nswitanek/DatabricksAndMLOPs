# Databricks notebook source
# MAGIC %md
# MAGIC # Validation of Home Purchase Price Analysis

# COMMAND ----------

import argparse
import os

from azureml.core import Run
from azureml.core.model import Model
from azureml.core.resource_configuration import ResourceConfiguration
from joblib import load
import pandas as pd

print("In validate_register.py")

parser = argparse.ArgumentParser("register")
parser.add_argument("--validation", type=str, help="validation data path")
parser.add_argument("--model", type=str, help="input model")
args = parser.parse_args()

print("Argument 1: %s" % args.model)

run = Run.get_context()
ws = run.experiment.workspace

MODEL_PATH = os.path.join(args.model, "model.joblib")

model = load(MODEL_PATH)
print(model)

dataset = run.input_datasets["validation"]
# load the TabularDataset to pandas DataFrame
df = dataset.to_pandas_dataframe()
print(df.shape)
print(df.head())

X = df.drop('y', axis=1)
y = df.y

pred = model.predict(X)

mse = mean_squared_error(y, pred)

# TODO: This should really be a dynamic query to see what the current threshold is
if mse <= 50.0:
    registered_model = Model.register(
        workspace=ws,
        model_name='my-sklearn-model',                # Name of the registered model in your workspace.
        model_path=MODEL_PATH,  # Local file to upload and register as a model.
        model_framework=Model.Framework.SCIKITLEARN,  # Framework used to create the model.
        model_framework_version='0.19.1',             # Version of scikit-learn used to create the model.
        resource_configuration=ResourceConfiguration(cpu=1, memory_in_gb=0.5),
        description='A sample model.',
        tags={'tag1': 'value1', 'tag2': 'value2'}
    )
    print(registered_model)
else:
    print("Model did not meet threshold for registration")
    print("MSE: {}".format(mse))

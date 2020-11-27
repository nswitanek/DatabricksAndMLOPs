# Databricks notebook source
# MAGIC %md
# MAGIC # Home Purchase Price Analysis

# COMMAND ----------

aml_inputs = dbutils.widgets.get("inputs")
aml_outputs = dbutils.widgets.get("outputs")

print(aml_inputs)
print(aml_outputs)

INPUT_PATH = aml_inputs["trainingcsv"]
OUTPUT_PATH = aml_outputs["output"]

# COMMAND ----------
import uuid

from pyspark.sql import functions as pyf
from pyspark.sql.types import *

# COMMAND ----------

schema = StructType([
  StructField('Year Built', StringType(), True),
  StructField('Bedrooms', IntegerType(), True),
  StructField('Bathrooms', DecimalType(), True),
  StructField('Square Footage', IntegerType(), True),
  StructField('AvgSchoolRanking', DecimalType(), True),
  StructField('LastSalePrice', DecimalType(), True)
])


# COMMAND ----------

# MAGIC %md
# MAGIC ### Data Processing

# COMMAND ----------

df = spark.read.csv(input_path, header=True, schema=schema)

df = (
    df
    .withColumnRenamed('LastSalePrice', 'y')
    .dropna()
)

df.cache()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Regression Modeling

# COMMAND ----------

from pyspark.ml.functions import vector_to_array
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.pipeline import Pipeline
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

categorical_columns = ['YearBuilt']
onehot_categorical_names = [f'oh{x}' for x in categorical_columns]
numeric_columns = []

string_indexers = [
  StringIndexer(inputCol=x, outputCol=f"si{x}", handleInvalid='keep')
  for x in categorical_columns
]

onehot = OneHotEncoder(
    inputCols=[f'si{x}' for x in categorical_columns], 
    outputCols=onehot_categorical_names,
    dropLast=True, 
)

va = VectorAssembler(
  inputCols=onehot_categorical_names + numeric_columns, 
  outputCol="features"
)

reg = LinearRegression(labelCol='y')

gridsearch = (
  ParamGridBuilder()
  .addGrid(reg.regParam, [0.0,1.0,10.0])
  .addGrid(reg.elasticNetParam, [0.0, 0.25, 0.5, 0.75, 1.0])
  .build()
)


pipe = Pipeline(stages= string_indexers + [onehot, va, reg] )

crossval = CrossValidator(
    estimator=pipe,
    estimatorParamMaps=gridsearch,
    evaluator=RegressionEvaluator(labelCol = 'y'),
    numFolds=3
)

cvFitted = crossval.fit(df)

preds = cvFitted.transform(df)
preds.cache()

# COMMAND ----------

resid = preds.withColumn("residuals", pyf.col("prediction") - pyf.col("y"))

# COMMAND ----------

cvFitted.avgMetrics

# COMMAND ----------

# MAGIC %md
# MAGIC ## Final Regression Model

# COMMAND ----------

best_params = {k.name:v for k, v in cvFitted.bestModel.stages[-1].extractParamMap().items()}
best_params

# COMMAND ----------

categorical_columns = ['YearBuilt']
onehot_categorical_names = [f'oh{x}' for x in categorical_columns]
numeric_columns = []

string_indexers = [
  StringIndexer(inputCol=x, outputCol=f"si{x}", handleInvalid='error')
  for x in categorical_columns
]

onehot = OneHotEncoder(
    inputCols=[f'si{x}' for x in categorical_columns], 
    outputCols=onehot_categorical_names,
    handleInvalid=True,
    dropLast=True, 
)

va = VectorAssembler(
  inputCols=onehot_categorical_names + numeric_columns, 
  outputCol="features"
)

reg = LinearRegression(**best_params)

final_ml_pipeline = Pipeline(stages= string_indexers + [onehot, va, reg] )

# COMMAND ----------

pipeFitted = final_ml_pipeline.fit(df)

# COMMAND ----------

df_predicted = (
    pipeFitted
    .transform(df)
    .withColumn("residuals", pyf.col("prediction") - pyf.col("y_WOTotal"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Extract Coefficients for Meta-Analysis

# COMMAND ----------

cols = []
print(pipeFitted.stages[-3].categorySizes)
print(sum(pipeFitted.stages[-3].categorySizes))
for stg in pipeFitted.stages:
  if "labels" in dir(stg):
    cols.extend(stg.labels[:-1])
    print(len(stg.labels))
  else:
    pass

print("=====")
print(len(cols))
print(len(pipeFitted.stages[-1].coefficients))
print("=====")
for coef, lbl in zip(pipeFitted.stages[-1].coefficients, cols):
  print(f"{lbl}\t{coef}")

print(f"Intercept: {pipeFitted.stages[-1].intercept}")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Evaluate Performance

# COMMAND ----------

mse = RegressionEvaluator(labelCol="y", metricName='mse')
mae = RegressionEvaluator(labelCol="y", metricName='mae')
rmse = RegressionEvaluator(labelCol="y", metricName='rmse')
r2 = RegressionEvaluator(labelCol="y", metricName='r2')
explvar = RegressionEvaluator(labelCol="y", metricName='var')

print(f"MSE: {mse.evaluate(df_predicted)}")
print(f"MAE: {mae.evaluate(df_predicted)}")
print(f"RMSE: {rmse.evaluate(df_predicted)}")
print(f"r2: {r2.evaluate(df_predicted)}")
print(f"var: {explvar.evaluate(df_predicted)}")

# COMMAND ----------

display(df_predicted.orderBy(pyf.abs("residuals")))

# COMMAND ----------

# MAGIC %md
# MAGIC #### Save Model

# COMMAND ----------

try:
    pipeFitted.save(output_path)
except:
    exception_guid = str(uuid.uuid4())
    exception_path = f"/modelException/{exception_guid}/model"
    print("An exception occurred while trying to save the model.")
    print(f"Saving here instead: {exception_path}")
    pipeFitted.save("/modelException/")

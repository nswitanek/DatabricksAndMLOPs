# Databricks notebook source
# MAGIC %md
# MAGIC # Functions for Model Training

# COMMAND ----------
from pyspark.sql import functions as pyf

def indexBedrooms(df, categoricals):
    temp_df = (
        df
        .groupBy(categoricals)
        .agg({'Bedrooms': 'avg'})
        .withColumnRenamed('avg(Bedrooms', 'annualBedroomAvg')
        .withColumn('bedroomIndex', pyf.col('Bedrooms') / pyf.col('annualBedroomAvg'))
    )
    out_df = df.join(temp_df, categoricals)
    return out_df
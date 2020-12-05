import traceback
import json
from azureml.core.model import Model
from pyspark.ml.pipeline import PipelineModel
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import DoubleType, StringType, IntegerType, DecimalType
from pyspark.sql import SQLContext
from pyspark import SparkContext

sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)
spark = sqlContext.sparkSession

schema = StructType([
  StructField('YearBuilt', StringType(), True),
  StructField('Bedrooms', IntegerType(), True),
  StructField('Bathrooms', DecimalType(), True),
  StructField('Square Footage', IntegerType(), True),
  StructField('AvgSchoolRanking', DecimalType(), True)
])
reader = spark.read
reader.schema(schema)


def init():
    global model
    # Get the model by name registered in Azure ML
    # This should get replaced by the devops pipeline
    model_path = Model.get_model_path('{{MODEL_NAME_TO_BE_REPLACED_BY_SED}}')
    model = PipelineModel.load(model_path)


def run(input_data):
    output = {}
    output["input"] = input_data
    try:
        input_dict = json.loads(input_data)
        input_df = reader.json(sc.parallelize(input_dict["data"]))
        result = model.transform(input_df)
        # you can return any datatype as long as it is JSON-serializable
        value = [p.asDict()['prediction'] for p in result.collect()]
        output["predictions"] = value
    except Exception as e:
        traceback.print_exc()
        error = str(e)
        output["error"] = error
    
    return output
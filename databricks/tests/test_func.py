from databricks.functions import *

from pyspark.sql import Row
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

from sparktestingbase.testcase import SparkTestingBaseTestCase
from sparktestingbase.sqltestcase import SQLTestCase

class FunctionsTest(SQLTestCase):
    """Test functions"""

    def test_index(self):
        """Test whether we can index bedrooms properly."""
        categorical_cols = ["colA"]
        input_data = [
            ["A",4],
            ["A",5],
            ["A",6],
        ]
        rdd = self.sc.parallelize(input_data)
        schema = StructType([
            StructField("colA", StringType(), True),
            StructField("Bedrooms", IntegerType(), True)
        ])

        df = self.sqlCtx.createDataFrame(rdd,schema)

        df_results = indexBedrooms(df, categorical_cols)

        rdd_results = df_results.select('bedroomIndex').orderBy('bedroomIndex').collect()
        results = [r.bedroomIndex for r in rdd_results]
        
        assert results == [0.8, 1.0, 1.2]
        
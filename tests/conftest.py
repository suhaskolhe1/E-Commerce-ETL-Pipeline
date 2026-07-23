import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    """Fixture for creating a local spark session for testing."""
    spark = SparkSession.builder \
        .appName("pytest-pyspark-local-testing") \
        .master("local[2]") \
        .getOrCreate()
    yield spark
    spark.stop()

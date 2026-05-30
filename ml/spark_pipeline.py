"""
Pipeline Spark NLP — Prétraitement du dataset Fake News
Projet IA & Big Data L3 — KENKOU Dave (Data Engineer)

Ce script crée le pipeline complet de prétraitement distribué
en utilisant Apache Spark et Spark NLP.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, lower, regexp_replace, concat_ws, lit, length,
    when, udf, trim, count, avg
)
from pyspark.sql.types import StringType, FloatType, IntegerType
import sparknlp
from sparknlp.base import DocumentAssembler, Pipeline
from sparknlp.annotator import (
    Tokenizer, Normalizer, StopWordsCleaner, LemmatizerModel
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_FAKE = "data/Fake.csv"
DATA_REAL = "data/True.csv"
OUTPUT_PATH = "data/processed/"


def create_spark_session():
    """Initialise la session Spark avec Spark NLP."""
    spark = SparkSession.builder \
        .appName("FakeNewsNLP-Pipeline") \
        .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:5.1.4") \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "8g") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info(f"Spark version: {spark.version}")
    return spark


def load_and_label_data(spark):
    """Charge les CSV Fake/Real et ajoute les labels."""
    logger.info(" Loading datasets...")
    df_fake = spark.read.csv(DATA_FAKE, header=True, inferSchema=True, multiLine=True, escape='"')
    df_real = spark.read.csv(DATA_REAL, header=True, inferSchema=True, multiLine=True, escape='"')

    df_fake = df_fake.withColumn("label", lit(0)).withColumn("label_str", lit("FAKE"))
    df_real = df_real.withColumn("label", lit(1)).withColumn("label_str", lit("REAL"))

    df = df_fake.union(df_real)
    logger.info(f"Total rows: {df.count()} | Schema: {df.columns}")
    return df


def eda_report(df):
    """Analyse exploratoire basique."""
    logger.info(" EDA Report:")
    df.groupBy("label_str").count().show()
    df.withColumn("text_length", length(col("text"))) \
      .groupBy("label_str") \
      .agg(avg("text_length").alias("avg_length")) \
      .show()
    df.groupBy("subject").count().orderBy("count", ascending=False).show(15)


def clean_text_pipeline(spark, df):
    """Pipeline de nettoyage avec Spark NLP."""
    logger.info(" Building NLP cleaning pipeline...")

    # 1. Basic cleaning with Spark SQL functions
    df_clean = df \
        .withColumn("text", regexp_replace(col("text"), r'<[^>]+>', '')) \
        .withColumn("text", regexp_replace(col("text"), r'https?://\S+', '[URL]')) \
        .withColumn("text", regexp_replace(col("text"), r'\s+', ' ')) \
        .withColumn("text", trim(col("text"))) \
        .withColumn("title", regexp_replace(col("title"), r'\s+', ' ')) \
        .withColumn("title", trim(col("title"))) \
        .filter(col("text").isNotNull()) \
        .filter(length(col("text")) > 50)

    # 2. Create combined feature: title + text (used for BERT input)
    df_clean = df_clean.withColumn(
        "content",
        concat_ws(" [SEP] ", col("title"), col("text"))
    )

    # 3. Compute engineered features
    df_clean = df_clean \
        .withColumn("text_length", length(col("text"))) \
        .withColumn("title_length", length(col("title"))) \
        .withColumn("has_url", when(col("text").contains("[URL]"), 1).otherwise(0)) \
        .withColumn("exclamation_count",
                    length(col("text")) - length(regexp_replace(col("text"), "!", "")))

    logger.info(f"After cleaning: {df_clean.count()} rows")
    return df_clean


def stratified_split(df):
    """Split stratifié 70/15/15."""
    logger.info("  Stratified split (70/15/15)...")
    fake_df = df.filter(col("label") == 0)
    real_df = df.filter(col("label") == 1)

    fake_train, fake_val, fake_test = fake_df.randomSplit([0.70, 0.15, 0.15], seed=42)
    real_train, real_val, real_test = real_df.randomSplit([0.70, 0.15, 0.15], seed=42)

    train = fake_train.union(real_train).orderBy("label")
    val   = fake_val.union(real_val).orderBy("label")
    test  = fake_test.union(real_test).orderBy("label")

    logger.info(f"Train: {train.count()} | Val: {val.count()} | Test: {test.count()}")
    return train, val, test


def save_splits(train, val, test):
    """Sauvegarde les splits au format Parquet (optimisé Big Data)."""
    logger.info(" Saving splits as Parquet...")
    cols = ["content", "title", "text", "label", "label_str",
            "text_length", "has_url", "exclamation_count"]

    train.select(cols).write.mode("overwrite").parquet(f"{OUTPUT_PATH}train")
    val.select(cols).write.mode("overwrite").parquet(f"{OUTPUT_PATH}val")
    test.select(cols).write.mode("overwrite").parquet(f"{OUTPUT_PATH}test")
    logger.info(f" Splits saved to {OUTPUT_PATH}")


def main():
    spark = create_spark_session()
    df = load_and_label_data(spark)
    eda_report(df)
    df_clean = clean_text_pipeline(spark, df)
    train, val, test = stratified_split(df_clean)
    save_splits(train, val, test)
    logger.info(" Pipeline completed successfully!")
    spark.stop()


if __name__ == "__main__":
    main()

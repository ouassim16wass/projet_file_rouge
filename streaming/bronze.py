import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, LongType, StringType, StructField, StructType

SCHEMA = StructType(
    [
        StructField("id_operation", LongType()),
        StructField("pas", IntegerType()),
        StructField("type", StringType()),
        StructField("montant", DoubleType()),
        StructField("emetteur", StringType()),
        StructField("solde_emetteur_avant", DoubleType()),
        StructField("solde_emetteur_apres", DoubleType()),
        StructField("destinataire", StringType()),
        StructField("solde_destinataire_avant", DoubleType()),
        StructField("solde_destinataire_apres", DoubleType()),
        StructField("est_fraude", IntegerType()),
    ]
)

SERVEUR = os.environ.get("KAFKA_SERVEUR", "kafka:29092")
TOPIC = os.environ.get("KAFKA_TOPIC", "operations.brutes")
SORTIE = os.environ.get("BRONZE_CHEMIN", "/donnees/bronze/operations")
CHECKPOINT = os.environ.get("BRONZE_CHECKPOINT", "/donnees/checkpoints/bronze")


def main():
    spark = SparkSession.builder.appName("guardpay-bronze").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    brut = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", SERVEUR)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "earliest")
        .option("maxOffsetsPerTrigger", 200000)
        .load()
    )

    bronze = brut.select(
        F.col("value").cast("string").alias("charge"),
        F.col("topic"),
        F.col("partition").alias("partition_kafka"),
        F.col("offset").alias("offset_kafka"),
        F.col("timestamp").alias("recu_a"),
    ).withColumn("evenement", F.from_json("charge", SCHEMA))

    ecriture = (
        bronze.select("evenement.*", "charge", "partition_kafka", "offset_kafka", "recu_a")
        .withColumn("date_ingestion", F.to_date("recu_a"))
        .writeStream.format("parquet")
        .option("path", SORTIE)
        .option("checkpointLocation", CHECKPOINT)
        .partitionBy("date_ingestion")
        .trigger(processingTime="10 seconds")
        .outputMode("append")
        .start()
    )
    ecriture.awaitTermination()


if __name__ == "__main__":
    main()

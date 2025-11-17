from pyspark.sql import DataFrame
from pyspark.sql.functions import col, aes_encrypt, aes_decrypt, base64, unbase64, lit, decode
from typing import List


class PIIEncryptionService:
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key
    
    def encrypt_pii_fields(self, df: DataFrame, pii_fields: List[str]) -> DataFrame:
        invalid_fields = [f for f in pii_fields if f not in df.columns]
        if invalid_fields:
            raise ValueError(f"Fields not found: {invalid_fields}")
        
        
        result_df = df
        result_df = result_df.withColumn("__encryption_key__", lit(self.encryption_key))
        for field in pii_fields:
            result_df = result_df.withColumn(
                field,
                base64(aes_encrypt(col(field), col("__encryption_key__")))
            )
        result_df = result_df.drop("__encryption_key__")
        return result_df
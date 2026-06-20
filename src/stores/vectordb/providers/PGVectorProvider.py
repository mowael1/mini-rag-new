from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import (DistanceMethodEnums, PgVectorTableSchemeEnums,
                            PGVectorDistanceMethodEnums, PgVectorIndexTypeEnums)
from ....models.db_schemes import RetrieveDocument
import logging

from sqlalchemy.sql import text as sql_text
import json

class PGVectorProvider(VectorDBInterface):
    
    
    def __init__(self, db_client, default_vector_size: int = 786,
                distance_method: str = None,
                index_threshold: int = 100):
        
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.distance_method = distance_method
        self.index_threshold = index_threshold
        
        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PERFIX.value
        self.logger = logging.getLogger("uvicorn")
        
        
    # ===================== Connection ===================== #
    # متفعله  pgvector دي وظيفتها بس اننا نتاكد ان ال 
    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                # هي الي بتنفذها session.execute وال SQLAlchemy عادي وتحولها هي ل raw sql دي هي بتاخد text عندك ال 
                await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))

    async def disconnect(self):
        # مفيش حاجة محتاجة تتقفل صريح - الـ session بتقفل نفسها كل مرة
        pass
    
    
    def get_collection_name(self, collection_name: str) -> str:
        # عشان الجدول ميتلخبطش مع جداول الـ projects/assets/chunks
        return f"{self.pgvector_table_prefix}_{collection_name}".strip()
    
    # دي غير الي البشمهندس عاملها
    async def is_collection_existed(self, collection_name: str) -> bool:
        table_name = self.get_collection_name(collection_name)

        async with self.db_client() as session:
            result = await session.execute(
                sql_text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :table_name)"
                ),
                {"table_name": table_name}
            )
            return result.scalar()
        
    async def list_all_collection(self) -> list:
        async with self.db_client() as session:
            result = await session.execute(
                sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix"),
                {"prefix": f"{self.pgvector_table_prefix}_%"}
            )
            return result.scalars().all()
        
        
    async def get_collection_info(self, collection_name: str) -> dict:
        table_name = self.get_collection_name(collection_name)

        async with self.db_client() as session:
            table_info_sql = sql_text("""
                SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                FROM pg_tables
                WHERE tablename = :table_name
            """)

            table_info = await session.execute(table_info_sql, {"table_name": table_name})
            table_data = table_info.fetchone()

            if table_data is None:
                return None

            # عدد الصفوف في الجدول
            count_result = await session.execute(sql_text(f"SELECT COUNT(*) FROM {table_name}"))
            records_count = count_result.scalar()

            return {
                "table_info": dict(table_data),
                "record_count": records_count
            }

    async def delete_collection(self, collection_name: str):
        table_name = self.get_collection_name(collection_name)

        async with self.db_client() as session:
            # insert, deleteزي ال tables في حاله انه في تغير هيصحل علي ال session.begin() بنستعمل ال 
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")
                await session.execute(sql_text(f"DROP TABLE IF EXISTS {table_name}"))

        return True
            
    async def create_collection(self, collection_name: str,
                                embedding_size: int, do_reset: bool = False):

        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)

        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.info(f"Creating collection: {collection_name}")
            table_name = self.get_collection_name(collection_name)

            async with self.db_client() as session:
                async with session.begin():
                    await session.execute(sql_text(
                        f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            {PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY,
                            {PgVectorTableSchemeEnums.TEXT.value} text,
                            {PgVectorTableSchemeEnums.Vector.value} vector({embedding_size}),
                            {PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT '{{}}'::jsonb,
                            {PgVectorTableSchemeEnums.CHUNK_ID.value} integer,
                            FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)

                        )
                        """
                    ))
            return True

        return False
        
    async def insert_one(self, collection_name: str, text: str, vector: list,
                        metadata: dict = None,
                        record_id: str = None):

        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if not record_id:
            self.logger.error(f"Can not insert new record without chunk_id: {collection_name}")
            return False
        
        table_name = self.get_collection_name(collection_name)

        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    f"""
                    INSERT INTO {table_name}
                        ({PgVectorTableSchemeEnums.TEXT.value},
                        {PgVectorTableSchemeEnums.Vector.value},
                        {PgVectorTableSchemeEnums.CHUNK_ID.value},
                        {PgVectorTableSchemeEnums.METADATA.value})
                    VALUES (:text, (:vector)::vector, :chunk_id, (:metadata)::jsonb)
                    """
                ), {
                    "text": text,
                    "vector": json.dumps(vector),
                    "chunk_id": record_id,
                    "metadata": json.dumps(metadata) if metadata else None,
                })
        
        return True
        
        
    async def insert_many(self, collection_name: str, texts: list, vectors: list,
                        metadata: list = None,
                        record_ids: list = None, batch_size: int = 50):

        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can not insert new records to non-existed collection: {collection_name}")
            return False
        
        if len(vectors) != len(record_ids):
            self.logger.error(f"Invalid data items for collection: {collection_name}")
            return False

        table_name = self.get_collection_name(collection_name)

        metadata = metadata or [None] * len(texts)
        record_ids = record_ids or [None] * len(texts)

        query = sql_text(
            f"""
            INSERT INTO {table_name}
                ({PgVectorTableSchemeEnums.TEXT.value},
                {PgVectorTableSchemeEnums.Vector.value},
                {PgVectorTableSchemeEnums.CHUNK_ID.value},
                {PgVectorTableSchemeEnums.METADATA.value})
            VALUES (:text, (:vector)::vector, :chunk_id, (:metadata)::jsonb)
            """
        )

        try:
            async with self.db_client() as session:
                async with session.begin():
                    for i in range(0, len(texts), batch_size):
                        batch_params = [
                            {
                                "text": t,
                                "vector": json.dumps(v),
                                "chunk_id": r_id,
                                "metadata": json.dumps(m) if m else None,
                            }
                            for t, v, m, r_id in zip(
                                texts[i:i + batch_size],
                                vectors[i:i + batch_size],
                                metadata[i:i + batch_size],
                                record_ids[i:i + batch_size],
                            )
                        ]
                        await session.execute(query, batch_params)

        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True
    
    
    # ===================== Indexing (lazy) ===================== #
    async def create_vector_index(self, collection_name: str):
        """
        بعد ما عدد الصفوف يعدي threshold معين، نعمل HNSW index
        - عمل index على جدول فاضي أو صغير مش مفيد، وممكن يأخر الـ insert من غير فايدة
        """
        table_name = self.get_collection_name(collection_name)

        async with self.db_client() as session:
            count_result = await session.execute(sql_text(f"SELECT COUNT(*) FROM {table_name}"))
            records_count = count_result.scalar()

            if records_count < self.index_threshold:
                return False

            index_name = f"{table_name}_vector_idx"

            exists_result = await session.execute(
                sql_text("SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = :index_name)"),
                {"index_name": index_name}
            )

            if exists_result.scalar():
                return False

            self.logger.info(f"START: Creating vector index for collection: {table_name}")
            async with session.begin():
                await session.execute(sql_text(
                    f"""
                    CREATE INDEX {index_name} ON {table_name}
                    USING {PgVectorIndexTypeEnums.HNSW.value}
                    ({PgVectorTableSchemeEnums.Vector.value} {self.distance_method})
                    """
                ))
            self.logger.info(f"END: Creating vector index for collection: {table_name}")
            
    async def reset_vector_index(self, collection_name: str):
            table_name = self.get_collection_name(collection_name)
            index_name = f"{table_name}_vector_idx"

            async with self.db_client() as session:
                async with session.begin():
                    await session.execute(sql_text(f"DROP INDEX IF EXISTS {index_name}"))

                await self.create_vector_index(collection_name=collection_name)

            return True
            

        
    # ===================== Search ===================== #

    async def search_by_vector(self, collection_name: str,
                                vector: list, limit: int = 5):

        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False

        table_name = self.get_collection_name(collection_name)

        # cosine distance operator <=> | L2 distance operator <->
        distance_operator = "<=>" if self.distance_method == PGVectorDistanceMethodEnums.COSINE.value else "<->"

        async with self.db_client() as session:
            result = await session.execute(sql_text(
                f"""
                SELECT {PgVectorTableSchemeEnums.TEXT.value} AS text,
                    1 - ({PgVectorTableSchemeEnums.Vector.value} {distance_operator} (:vector)::vector) AS score
                FROM {table_name}
                ORDER BY {PgVectorTableSchemeEnums.Vector.value} {distance_operator} (:vector)::vector DESC
                LIMIT :limit
                """
            ), {"vector": json.dumps(vector), "limit": limit})

            records = result.fetchall()

        if not records:
            return None

        return [
            RetrieveDocument(text=record.text, score=record.score)
            for record in records
        ]
        
        
        
        
        
    
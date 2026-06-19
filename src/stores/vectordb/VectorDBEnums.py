from enum import Enum

class VectorDBType(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"
    
    
class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"
    

class PgVectorTableSchemeEnums(Enum):
    ID = "id"
    TEXT = "text"
    Vector = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PERFIX = "pgvector"
        
class PGVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"
    
# يعني لو عندك مليون هيروح يلف عليهم واحد واحدgreedy بيروح يدور بالطريقه ال pgvector ال vectordb دي وهو بيدور في ال 
# hnsw بيستعملها هي ال qdrant لكن الطريقه التانيه والاسرع والي ال 
# واحد بيمثلها vector الي عندك الي مجموعات وكل مجموعه بيكون ليها embeddings والي هي عبارة عن انك بتقسم ال 
# وجوه كل مجموعه بيكون في طبقه تانيه بردو متقسمه الي مجموعات 
class PgVectorIndexTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"
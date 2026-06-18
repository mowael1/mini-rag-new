from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class Asset(SQLAlchemyBase):
    
    __tablename__ = "assets"
    
    asset_id = Column(type_=Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(UUID, default= uuid.uuid4, unique= True, nullable=False)
    
    asset_type = Column(String , nullable=False)
    asset_name = Column(String , nullable=False)
    asset_size = Column(Integer , nullable=False)
    
    # metadata الي بيكون فيه ال json file الخاص بانه يشيل column ده ال 
    asset_config = Column(JSONB , nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),nullable=True)
    
    # الي هنربط من خلاله الجداول مع بعضforiegn key دي الي هو 
    # project_id الي اسمه column ويربطه بال projects الي اسمه table ده كده هو هيروح يدور علي ال 
    asset_project_id = Column(Integer, ForeignKey("projects.project_id"),nullable=False)
    
    
    # فيها column ومتكونش database في ال attributes نقدر بقي اننا نعمل     
    project = relationship("Project", back_populates="assets")
    chunks = relationship("DataChunk", back_populates="assets")
    
    
    # foreign key علي ال indexing وهحتاج اني اعمل 
    # indexing هو اتوماتيك بيعمل عليهم foreign key او ال unique = true واي حاجه انت بتعملها 
    
    # indexing في طريقتين عشان تعمل بيهم 
    # index=True الي اسمه parameter اما انك تروح مباشر تديله 
    #  __table_args__ او انك تستعمل 
    
    __table_args__ = (
        Index("ix_asset_project_id",asset_project_id),
        Index("ix_asset_type",asset_type)
    )
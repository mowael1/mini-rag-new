from src.models.BaseDataModel import BaseDataModel
from src.models.enums.DataBaseEnum import DataBaseEnum
from src.models.db_schemes import Asset
from bson.objectid import ObjectId

from sqlalchemy import select, func


class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client
        
    #==========================================================#            
    # ده collection دي بقي الي انت هتستعملها عشان تعمل ال 
    # فعملنا دي كحاجه وسيطه __init__ مينفعش اننا نضيفها جوه ال async function ودي عملناها لان ال 
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)        
        return instance
    #==========================================================#
    # asset بيها create ن function دلوقتي بقي عاوزين نعمل 
    async def create_asset(self, asset: Asset):
        
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)

            await session.refresh(asset)

        return asset
    
    # الي هندهوله project_idبتاعت ال assets تانيه تجيب كل ال function و 
    async def get_all_project_assets(self,asset_project_id: str, asset_type: str):
        
        async with self.db_client() as session:

            result = await session.execute(
                select(Asset).where(
                    Asset.asset_project_id == asset_project_id,
                    Asset.asset_type == asset_type
                )
            )

            assets = result.scalars().all()

        return assets
        
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        
        async with self.db_client() as session:

            result = await session.execute(
                select(Asset).where(
                    Asset.asset_project_id == asset_project_id,
                    Asset.asset_name == asset_name
                )
            )

            asset = result.scalar_one_or_none()

        return asset
from src.models.BaseDataModel import BaseDataModel
from src.models.enums.DataBaseEnum import DataBaseEnum
from src.models.db_schemes.asset import Asset
from bson.objectid import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        
        # asset الي اسمه collection بتاعتك وبتدور علي database علي ال connection ده كده هو بيعملك 
        # self.collection ويبدا انه يخزنه جوه ال 
        # هينشاه اتوماتيك insert ولو مش موجود هو مع اول 
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
        
    #==========================================================#
    # indexing هنا بقي هنبدا اننا نضيف ال 

    # indexes الي هتضيف لينا ال function فاول حاجه احنا عملنا ال 
    # ده collection وهنبقي عاوزين اننا نستدعيها اول ما ننشا ال 
    async def init_collection(self):
        indexes = Asset.get_indexs()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
            
    # ده collection دي بقي الي انت هتستعملها عشان تعمل ال 
    # فعملنا دي كحاجه وسيطه __init__ مينفعش اننا نضيفها جوه ال async function ودي عملناها لان ال 
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        
        return instance
    #==========================================================#
    # asset بيها create ن function دلوقتي بقي عاوزين نعمل 
    async def create_asset(self, asset: Asset):
        
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        
        return asset
    
    # الي هندهوله project_idبتاعت ال assets تانيه تجيب كل ال function و 
    async def get_all_project_assets(self,asset_project_id: str, asset_type: str):
        
        records =  await self.collection.find({
            # ObjectId بس ده عشان يدور بيه لازم يكون 
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_type": asset_type
        }).to_list(length = None)
        
        return [
            Asset(**record)
            for record in records
        ]
        
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_name": asset_name
        })
        
        if record: 
            return Asset(**record)
        
        return None
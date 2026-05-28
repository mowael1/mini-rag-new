from src.models.BaseDataModel import BaseDataModel
from src.models.enums.DataBaseEnum import DataBaseEnum
from src.models.db_schemes.asset import Asset

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        
        # asset الي اسمه collection بتاعتك وبتدور علي database علي ال connection ده كده هو بيعملك 
        # self.collection ويبدا انه يخزنه جوه ال 
        # هينشاه اتوماتيك insert ولو مش موجود هو مع اول 
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
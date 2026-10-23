from abc import abstractmethod,ABC
from uuid import UUID
from app.schemas.refresh_token import RefreshToken

class AbstractRefreshTokenRepository(ABC):
    @abstractmethod
    async def create_token(self,token:RefreshToken)->None:...
    
    @abstractmethod
    async def get_token_by_id(self,token_id:UUID)->RefreshToken|None:...
    
    @abstractmethod
    async def get_token_by_hash(self,hash_token:str)->RefreshToken|None:...
    
    @abstractmethod
    async def revoke_all_tokens_by_family_id(self,family_id:UUID)->None:...
    
    @abstractmethod
    async def save(self,token:RefreshToken)->None:...
    
    @abstractmethod
    async def delete(self,token_id:UUID)->None:...
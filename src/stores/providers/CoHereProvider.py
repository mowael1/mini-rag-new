from ..llm.LLMInterface import LLMInterface
from ..llm.LLMEnums import CoHereEnums ,DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):
    
    def __init__(self, api_key: str,
                default_input_max_char: int= 1000,
                default_generation_max_output_tokens: int= 1000,
                defult_generation_temperature: float = .1):
        
        self.api_key = api_key
        
        self.default_input_max_char = default_input_max_char
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.defult_generation_temperature = defult_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.ClientV2(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    def process_text(self, text: str):
        return text[:self.default_input_max_char].strip()
    
    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self.process_text(prompt)}
    
    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float= None):
        
        # موجود ولا لاclient لازم الاول تشيك هل ال 
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        # موجود generation الي هنستعمل في ال model اتاكد ان ال 
        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.defult_generation_temperature
        
        chat_history.append(self.construct_prompt(prompt=prompt, role=CoHereEnums.USER.value))
        
        response = self.client.chat(
            model=self.generation_model_id,
            messages=chat_history,
            temperature=temperature,
            max_tokens=max_output_tokens
        )
        
        if not response or not response.message or not response.message.content or len(response.message.content) == 0:
            self.logger.error("Error while generating text with Cohere")
            return None

        return response.message.content[0].text
    

    def embed_text(self, text: str, document_type: str= None):

        # موجود ولا لاclient لازم الاول تشيك هل ال 
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        
        # اصلا embedding عشان لو مش موجود مش هعرف اعمل embedding_model_id وبردو اشيك علي ال 
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere was not set")
            return None
        
        input_type = None
        if document_type == DocumentTypeEnum.DOCUMENT.value:
            input_type = CoHereEnums.DOCUMENT.value
        elif document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=["float"]
        )
        
        if not response or not response.embeddings or not response.embeddings.float or len(response.embeddings.float) == 0:
            self.logger.error("Error while embedding text with Cohere")
            return None
        
        return response.embeddings.float[0]
from ..llm.LLMInterface import LLMInterface
from ..llm.LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

# بتاعته عادي __init__() هيكون ليه ال providers كل واحد بقي من ال 
class OpenAIProvider(LLMInterface):
    
    # openai الي هتجيبه من ال api_key ال 
    # علي حاجه تانيه من خلاله accessمن حته تانيه فعشان كده ده بيوفرلك انك تعمل model لانك ممكن تجيب optional ده بيكون api_url وال 
    
    # ليه maximum فكان لازم نحط tokens وبالتالي تضيع كل chunk كله بدل ال document ده عشان ممكن يحصل غلطه وتلاقي نفسك باعتله inpu_max_char ال 
    # outputنفس الكلام لازم نطبقه علي ال 
    
    def __init__(self, api_key: str, api_url: str= None,
                default_input_max_char: int= 1000,
                default_generation_max_output_tokens: int= 1000,
                defult_generation_temperature: float = .1):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.default_input_max_char = default_input_max_char
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.defult_generation_temperature = defult_generation_temperature
        
        # embedding , generationدلوقتي والي هما ال two tasks في openai هستعمل ال 
        # vector databaseلاننا هنبقي محتاجينه في ال embedding size لازم اخد كمان ال embedding ومع ال 
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        # client لازم انك تعرف openai عشان تبدا تتعامل مع 
        self.client = OpenAI(
            api_key= self.api_key,
            api_url= self.api_url,
        )
        
        # loggingمنه يبدا انه يكون عندنا معملومات في ال object ده عشان كلما ناخد class في ال logger هنعمل 
        # logger فاي رساله انا عاوز اطبعها هيكون من خلال ال 
        
        # الي هو موجود فيه file كده هو هاخد اسم ال 
        self.logger = logging.getLogger(__name__)
        
        
    # بتاعها logic ونحط ال interface الي موجوده في ال functions هنبدا بقي دلوقتي نجيب ال 
    # instructor تحطه في model_id ودي كل الي هتعملوا دلوقتي انها هتاخد ال 
    # شغال فعلا علي السيرفر client في اي وقت اثناء من ال model وحطيناه هنا لاننا ممكن نغير ال 
    # يبقي كنا هنثبت عليه ومش هنقدر اننا نغيره بعد كده__init__ فلو كنا حطيناه في ال 
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    
    # تانيه من الاساسين function ولكنها هتكون مساعده او هنستعملها في interface دي مهياش موجوده في ال 
    def process_text(self, text: str):
        return text[:self.default_input_max_char].strip()
        
    
    # بيتعامل بيه API عشان ده الي ال chat completions يتبعت تحوله للشكل بتاع ال prompt دي المسؤله ان اي 
    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self.process_text(prompt)}

    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float= None):
        
    # موجود ولا لاclient لازم الاول تشيك هل ال 
        if not self.client:
            self.logger.error("OpenAI was not set")
            return None
        
        # موجود generation الي هنستعمل في ال model اتاكد ان ال 
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.defult_generation_temperature
        
        # LLM بتاع ال API دي كلها بعد كده ونبعتها ل list الي هناخد ال user هتكون هي الرساله بتاعت ال chat_history وان اخر رساله في ال 
        chat_history.append(self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value))
        
        response = self.client.chat.completions.create(
            model=self.embedding_model_id,
            messages=chat_history,
            max_tokens=self.max_output_tokens,
            temperature=temperature)
        
        # الي راجع ده هل هو مضبوط ولا فيه مشاكلresponse بعد كده لازم اشيك علي ال 
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message["content"]

    
    def embed_text(self, text: str, document_type: str= None):

        # موجود ولا لاclient لازم الاول تشيك هل ال 
        if not self.client:
            self.logger.error("OpenAI was not set")
            return None
        
        # اصلا embedding عشان لو مش موجود مش هعرف اعمل embedding_model_id وبردو اشيك علي ال 
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        # data ل embedding لو خلاص الاتنين الي فوق تمام يبقي هروح اعمل 
        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input = text
        )
        
        # الي داخل input بتاع ال embedding الي هو ال response عاوز بقي انا اشيك علي ال 
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        # embedding وخلاص لو عدي بقي يبقي يرجع ال 
        return response.data[0].embedding
    
        
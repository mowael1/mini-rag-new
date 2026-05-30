# يعني مش حاجه هتشتغلabstract class بما اننا هنعمل 
# abstract الي جوه هي كمان هتكون functions عشان الabstract فهنستعمل ال 
# دي functions هيورث من ده لازم يعمل ال class يعني اي 

# هتفضل فاضيه logic الي مش هتكون بتنفذ اي functions فيه مجموعه من ال class هو اننا بيكون عندنا interface ويبقي الفكره بتاعت ال 
# ده بعد كده interface الي هيورث من ال class واحنا بس بنعمل شكل عشان ال 

#  class يكون وظيفته انه يكون شكل لل logic يكون فيه مجموعه من ال بدون اي class هو اننا نعمل interface ويبقي الفكره بتاعت ال 
from abc import ABC, abstractmethod

class LLMInterface(ABC):
    
    # دي function الي هيورث من ده بعد كده انه ينفذ ال class ده وظيفته انه يجبر ال decorator ال 
    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass
    
    @abstractmethod
    def set_embedding_model(self, model_id: str):
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, max_output_tokens: int, temperature: float= None):
        pass
    
    # generate_text دي عشان يعدله ويظبطه قبل ما يديه مثلا ل function يجي يدخل علي ال prompt دي عشان اي 
    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str):
        pass
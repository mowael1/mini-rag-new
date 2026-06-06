import os
# runtime اثناء ال file(module) دي الي من خلالها هتجيب 
import importlib

class TemplateParser:
    
    def __init__(self, language: str = None, default_language = "en"):
        
        # الي موجود فيه دلوقتيfile بتاع ال path وظيفتها انها تجبلي ال os.path.abspath(__file__) دي 
        # بتاعه directory path ده وتجبلك ال path هتاخد ال os.path.dirname()وال 
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        
        self.set_language(language)
        
    def set_language(self, language: str):
        
        if not language: 
            self.language = self.default_language
        
        language_path = os.path.join(
            self.current_path,
            "locales",
            language
        )
        if os.path.exists(language_path):
            self.language = language
            
        else:
            self.language = self.default_language
            
    def get(self, group: str, key: str, vars: dict={}):
        
        # group: is rag.py file
        if not group or not key: 
            return None
        
        group_path = os.path.join(
            self.current_path,
            "locales",
            self.language,
            f"{group}.py"
        )
        
        targeted_lang = self.language
        
        if not os.path.exists(group_path): 
            group_path = os.path.join(
                self.current_path,
                "locales",
                self.default_language,
                f"{group}.py"
            )
            
            targeted_lang = self.default_language
            
        if not os.path.exists(group_path): 
            return None
        
        
        #import group module
        module = importlib.import_module(f"src.stores.llm.templates.locales.{targeted_lang}.{group}")
        
        
        # system_prompt , document_prompt زي ال rag.py والي هو جزه الkey هنبدا بقي اننا نجيب ال 
        if not module:
            return None
        
        key_attribute = getattr(module, key)
        
        return key_attribute.substitute(vars)
from typing import Any, Dict, List, Optional
from omegaconf import OmegaConf


from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable



from llm_miner.config import config
from llm_miner.reader import JournalReader
from llm_miner.categorize.base import CategorizeAgent
from llm_miner.text.base import TextMiningAgent
from llm_miner.error import BaseMiningError
from llm_miner.meta_collector import MetaCollector
from llm_miner.pricing import TokenChecker
from llm_miner.local_model_factory import LocalModelFactory





class LLMMiner(Runnable):
    categorize_agent: Runnable
    property_agent: Runnable
    input_key: str = "paragraph"
    output_key: str = "output"
    verbose: bool = False
    
    def __init__(self, categorize_agent: Runnable, property_agent: Runnable, verbose: bool = False):
        super().__init__()
        self.categorize_agent = categorize_agent
        self.property_agent = property_agent
        self.verbose = verbose

    @property
    def input_schema(self):
        return {"type": "object", "properties": {self.input_key: {"type": "string"}}}

    @property
    def output_schema(self):
        return {"type": "object", "properties": {self.output_key: {"type": "string"}}}

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]




    def run(self, journal_reader, **kwargs):
        """Run the agent on a JournalReader with optional parameters."""
        config = kwargs.copy()
        config["reconstruct"] = config.get("reconstruct", True)
        
        # Handle both JournalReader directly and dict inputs for compatibility
        if isinstance(journal_reader, dict):
            # If already a dict, add the journal_reader to the appropriate key
            inputs = journal_reader.copy()
            if self.input_key not in inputs:
                inputs[self.input_key] = journal_reader
        else:
            # If JournalReader, wrap it in the expected dict format
            inputs = {self.input_key: journal_reader}
            
        return self.invoke(inputs, config=config)

    def _parse_output(self, output: str) -> Dict[str, str]:
        raise NotImplementedError()

    def invoke(
        self,
        inputs: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Simplified for Runnable interface

        jr: JournalReader = inputs[self.input_key]
        token_checker: TokenChecker = inputs.get("token_checker")

        for element in jr.elements:
            try:
                # Progress log: indicate which paragraph we're categorizing
                print(f"[LLMMiner] Categorizing paragraph (id={getattr(element, 'id', 'n/a')})...")
                categories = self.categorize_agent.invoke(
                    {"paragraph": element},
                )
                print(f"[LLMMiner] Categorization complete (id={getattr(element, 'id', 'n/a')})")
            except BaseMiningError:
                element.classification = "error"

            # print (categories)

        # reconstruct elements -> merge paragraph for reducing tokens
        if config.get("reconstruct"):
            jr.reconstruct()


        for element in jr.get_properties():
            try:
                # Pass properties_only flag to property agent
                property_inputs = {"element": element}
                if config.get("properties_only"):
                    property_inputs["properties_only"] = True
                # Progress log: start extraction for this element
                print(f"[LLMMiner] Extracting properties for element (id={getattr(element, 'id', 'n/a')})...")
                output = self.property_agent.invoke(property_inputs)
                print(f"[LLMMiner] Extraction complete (id={getattr(element, 'id', 'n/a')})")
            except BaseMiningError as e:
                element.set_data([str(e)])
            else:
                pass
                # print (output)

        mc = MetaCollector.from_journal_reader(jr)
        jr.result = mc.run()

        if config["reconstruct"]:
            # mc = MetaCollector.from_elements(jr.cln_elements)
            # jr.result = mc.run()
            return {self.output_key: jr.cln_elements}
        else:
            # mc = MetaCollector.from_elements(jr.elements)
            # jr.result = mc.run()
            return {self.output_key: jr.elements}

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        simple_llm: BaseLanguageModel,
        *,
        ft_model_dict: Optional[Dict[str, BaseLanguageModel]] = None,
        **kwargs,
    ) -> Runnable:
        if ft_model_dict is None:
            ft_model_dict = dict()

        categorize_agent = CategorizeAgent.from_llm(
            llm=ft_model_dict.get("ft_text_categorize", simple_llm), **kwargs
        )


        property_agent = TextMiningAgent.from_llm(
            type_llm=ft_model_dict.get("ft_text_property_type", llm),
            extract_llm=ft_model_dict.get("ft_text_property_extract", llm),
            properties_only=kwargs.get("properties_only", False),
            **kwargs,
        )



        return cls(
            categorize_agent=categorize_agent,
            property_agent=property_agent,
            verbose=kwargs.get("verbose", False)
        )

    @classmethod
    def from_yaml(
        cls,
        yaml: str,
        openai_api_key: str = None,
    ) -> Runnable:
        config = OmegaConf.load(yaml)
        return cls.from_config(dict(config), openai_api_key=openai_api_key)


    @classmethod
    def from_config(
        cls,
        config: Dict[str, Any],
        openai_api_key: str = None,
    ) -> Runnable:
        # Check if local models should be used
        use_local = config.get("use_local_models", False)
        
        if use_local:
            print("🔧 Using local models configuration...")
            
            # Get local models from factory
            local_categorizer = LocalModelFactory.get_text_categorizer()
            local_property_type = LocalModelFactory.get_text_property_type()
            local_property_extract = LocalModelFactory.get_text_property_extract()
            
            # Prepare ft_model_dict with local models
            ft_model_dict = {}
            
            if local_categorizer:
                ft_model_dict["ft_text_categorize"] = local_categorizer
                print("✓ Loaded local text categorizer")
            
            if local_property_type:
                ft_model_dict["ft_text_property_type"] = local_property_type
                print("✓ Loaded local property type classifier")
            
            if local_property_extract:
                ft_model_dict["ft_text_property_extract"] = local_property_extract
                print("✓ Loaded local property extract model")
            
            # Use simple fallback LLMs for any missing models
            simple_llm = ChatOpenAI(
                model_name=config["simple_model_name"],
                temperature=config["temperature"],
                openai_api_key=openai_api_key,
            )
            
            # Use simple_llm as fallback for missing local models
            if "ft_text_categorize" not in ft_model_dict:
                ft_model_dict["ft_text_categorize"] = simple_llm
                print("⚠️ Using fallback model for text categorization")
                
            if "ft_text_property_type" not in ft_model_dict:
                ft_model_dict["ft_text_property_type"] = simple_llm
                print("⚠️ Using fallback model for property type classification")
                
            # Always use simple_llm for extraction (no local model available)
            ft_model_dict["ft_text_property_extract"] = simple_llm
            
        else:
            # Original OpenAI model configuration
            llm = ChatOpenAI(
                model_name=config["model_name"],
                temperature=config["temperature"],
                openai_api_key=openai_api_key,
            )
            simple_llm = ChatOpenAI(
                model_name=config["simple_model_name"],
                temperature=config["temperature"],
                openai_api_key=openai_api_key,
            )

            # fine-tuned model
            ft_model_dict = {
                ft_name: ChatOpenAI(
                    model_name=ft_model,
                    temperature=config["temperature"],
                    openai_api_key=openai_api_key,
                )
                for ft_name, ft_model in config["fine_tuning_models"].items()
                if ft_model
            }
            
            # Add fallback models
            ft_model_dict.setdefault("ft_text_categorize", simple_llm)
            ft_model_dict.setdefault("ft_text_property_type", llm)
            ft_model_dict.setdefault("ft_text_property_extract", llm)

        return cls.from_llm(
            llm=ChatOpenAI(
                model_name=config["model_name"],
                temperature=config["temperature"],
                openai_api_key=openai_api_key,
            ),
            simple_llm=ChatOpenAI(
                model_name=config["simple_model_name"],
                temperature=config["temperature"],
                openai_api_key=openai_api_key,
            ),
            ft_model_dict=ft_model_dict,
            verbose=config["verbose"],
        )

    @classmethod
    def create(cls, openai_api_key=None):
        """Auto creation using config (default)"""
        return cls.from_config(config, openai_api_key)

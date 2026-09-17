
import ast
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable





from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


from llm_miner.categorize.prompt import PROMPT_CATEGORIZE, FT_CATEGORIZE, FT_HUMAN
from llm_miner.error import StructuredFormatError, ContextError, LangchainError
from llm_miner.schema import Paragraph
from llm_miner.pricing import TokenChecker, update_token_checker
from llm_miner.local_model_factory import LocalModelFactory
from llm_miner.config import config
import concurrent.futures





class CategorizeAgent(Runnable):
    categorize_chain: Runnable
    labels: List[str] = ["battery", "non battery"]
    input_key: str = "paragraph"
    output_key: str = "output"
    

    def __init__(self, categorize_chain: Runnable, labels: List[str] = None):
        super().__init__()
        self.categorize_chain = categorize_chain
        if labels is not None:
            self.labels = labels

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    

    def _write_log(self, text: str, run_manager=None):
        print(f"\n[Categorize] {text}")

    def _parse_output(self, output: str) -> Dict[str, str]:
        output = output.replace("List:", "").strip()  # remove `List`
        try:
            return ast.literal_eval(output)
        except Exception as e:
            raise StructuredFormatError(e)
    


    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        para: Paragraph = inputs[self.input_key]
        token_checker: TokenChecker = inputs.get('token_checker')

        if para.type in self.labels:
            self._write_log([para.type], None)
            return {self.output_key: [para.type]}
        
        llm_kwargs={
            'paragraph': str(para.content),
        }
        try:
            # Use invoke for Runnable interface without callbacks
            timeout = config.get("llm_request_timeout", 60)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(self.categorize_chain.invoke, llm_kwargs, {"stop": ["List:"]})
                llm_output = fut.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            para.add_intermediate_step('categorize', f'Timeout after {timeout}s')
            raise LangchainError(f'LLM categorize call timed out after {timeout}s')
        except Exception as e:
            para.add_intermediate_step('categorize', str(e))
            raise LangchainError(e)
        else:
            para.add_intermediate_step('categorize', llm_output)

        if token_checker:
            update_token_checker(
                name_step='categorize',
                chain=self.categorize_chain,
                token_checker=token_checker,
                llm_kwargs=llm_kwargs,
                llm_output=llm_output
            )
        output = self._parse_output(llm_output)
        para.set_classification(output)

        if not output:
            para.add_intermediate_step('categorize-parsing', 'no categories error')
            raise ContextError(f"There are no categories in paragraph")
        if any([v not in self.labels for v in output]):
            para.add_intermediate_step('categorize-parsing', 'not included error')
            raise ContextError(f"Class of paragraph must be one of {self.labels}, not {output}")

        self._write_log(str(output), None)

        return {self.output_key: output}
    


    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        prompt: str = PROMPT_CATEGORIZE,
        ft_prompt: str = FT_CATEGORIZE,
        ft_human: str = FT_HUMAN,
        **kwargs,
    ) -> Runnable:
        
        # Try to use local model first if enabled
        local_categorizer = LocalModelFactory.get_text_categorizer()
        
        if local_categorizer:
            print("Using local FLAN-T5 text categorizer model")
            # For local models, we don't need prompts since they're fine-tuned
            # The local model wrapper handles the prompt internally
            prompt_template = PromptTemplate(template="classify paragraph: {paragraph}", input_variables=["paragraph"])
            categorize_chain = prompt_template | local_categorizer | StrOutputParser()
        elif llm.model_name.startswith('ft:'): # fine-tuned model
            system_prompt = SystemMessagePromptTemplate.from_template(ft_prompt)
            human_prompt = HumanMessagePromptTemplate.from_template(ft_human)
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_prompt, human_prompt]
            )
            categorize_chain = chat_prompt | llm | StrOutputParser()
        else:  # gpt base model
            template = PromptTemplate(
                template=prompt,
                input_variables=["paragraph"],
            )
            categorize_chain = template | llm | StrOutputParser()


        return cls(categorize_chain=categorize_chain)

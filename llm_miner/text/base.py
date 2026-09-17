import ast
import regex
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


from llm_miner.text.prompt import PROMPT_TYPE, PROMPT_EXT, FT_TYPE, FT_HUMAN
from llm_miner.schema import Paragraph
from llm_miner.format import Formatter
from llm_miner.format.formatter import PropertiesOnlyFormatter
from llm_miner.error import StructuredFormatError, LangchainError, TokenLimitError
from llm_miner.pricing import TokenChecker, update_token_checker
from llm_miner.local_model_factory import LocalModelFactory
from llm_miner.config import config
import concurrent.futures






class TextMiningAgent(Runnable):
    type_chain: Runnable
    extract_chain: Runnable
    input_key: str = "element"
    output_key: str = "output"
    properties_only: bool = False
    

    def __init__(self, type_chain: Runnable, extract_chain: Runnable, properties_only: bool = False):
        super().__init__()
        self.type_chain = type_chain
        self.extract_chain = extract_chain
        self.properties_only = properties_only

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    

    def _write_log(self, text: str, run_manager=None):
        print(f"\n[Property Mining] {text}")

    def _parse_output(self, output: str) -> Dict[str, str]:
        if regex.search(r"^\s*```JSON", output) and not regex.search(r"```\s*$", output):
            raise TokenLimitError('Output does not finished before token limits', output)
        
        output = output.replace("```JSON","")
        output = output.replace("```","")
        output = output.strip()
        if regex.search(r"[Ii] do not know", output):
            return [output]
        try:
            return ast.literal_eval(output)
        except Exception as e:
            raise StructuredFormatError(e, output)
    

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        explanation = self._add_explanation()
        element: Paragraph = inputs[self.input_key]
        token_checker: TokenChecker = inputs.get('token_checker')
        paragraph: str = element.clean_text   # change content -> clean_text

        llm_kwargs = {
            'explanation': explanation,
            'paragraph': paragraph,
        }

        try:
            timeout = config.get("llm_request_timeout", 60)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(self.type_chain.invoke, llm_kwargs, {"stop": ["Paragraph:"]})
                llm_output = fut.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            element.add_intermediate_step('text-property-type', f'Timeout after {timeout}s')
            raise LangchainError(f'LLM text-property-type call timed out after {timeout}s')
        except Exception as e:
            element.add_intermediate_step('text-property-type', str(e))
            raise LangchainError(e)
        else:
            element.add_intermediate_step('text-property-type', llm_output)

        if token_checker:
            update_token_checker(
                name_step='text-property-type',
                chain=self.type_chain,
                token_checker=token_checker, 
                llm_kwargs=llm_kwargs, 
                llm_output=llm_output
            )

        property_type = self._parse_output(llm_output)
        self._write_log(str(property_type), None)
        element.set_include_properties(property_type)


        st_data_string = ""
        info_string = ""
        example_string = ""
        prop_string = ""

        # Use PropertiesOnlyFormatter if properties_only mode is enabled
        if self.properties_only:
            formatter = PropertiesOnlyFormatter
        else:
            formatter = Formatter

        for prop in property_type:
            try:
                st_data = formatter.structured_data[prop]
                info = formatter.information[prop]
                example = formatter.example_text[prop]
            except KeyError:
                self._write_log(f"There are no format for {prop}", None)
                continue

            st_data_string += f"- {st_data}\n"
            info_string += f"- {info}\n"
            example_string += f"- {example}\n"
            prop_string += f"{prop}, "

        llm_kwargs={
            'prop': prop_string,
            'structured_data': st_data_string,
            'information': info_string,
            'example': example_string,
            'paragraph': paragraph,
        }

        try:
            timeout = config.get("llm_request_timeout", 60)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(self.extract_chain.invoke, llm_kwargs, {"stop": ["Paragraph:"]})
                llm_output = fut.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            element.add_intermediate_step('text-property-extract', f'Timeout after {timeout}s')
            raise LangchainError(f'LLM text-property-extract call timed out after {timeout}s')
        except Exception as e:
            element.add_intermediate_step('text-property-extract', str(e))
            raise LangchainError(e)
        else:
            element.add_intermediate_step('text-property-extract', llm_output)
            
        if token_checker:
            update_token_checker(
                name_step='text-property-extract',
                chain=self.extract_chain,
                token_checker=token_checker, 
                llm_kwargs=llm_kwargs, 
                llm_output=llm_output
            )

        st_output = self._parse_output(llm_output)
        # Post-process parsed structured output: try to infer missing units
        # from the paragraph text when the model returns values without
        # explicit units. This helps salvage unit information when the
        # LLM omits units but the original paragraph contains them.
        def _normalize_number_str(s: str) -> str:
            return str(s).strip().replace(',', '.')

        def _infer_unit_from_text(value_str: str, text: str) -> Optional[str]:
            # Look for the value in the text and capture an immediate unit
            # token after or before the value. We allow common unit
            # characters and stop at punctuation/newline.
            try:
                vs = _normalize_number_str(value_str)
            except Exception:
                vs = str(value_str)

            # Try exact match (with optional whitespace) followed by unit
            pattern_after = rf"{regex.escape(vs)}\s*(?P<unit>[%°μµ‰A-Za-zΩΩ/\u00B2\u00B3\u00B5\-\.\u00B0\w\u00B5\u00B2\u00B3]+)"
            m = regex.search(pattern_after, text)
            if m:
                return m.group('unit').strip()

            # Try match where unit precedes the number (e.g., "mAh/g 170")
            pattern_before = rf"(?P<unit>[%°μµ‰A-Za-zΩΩ/\u00B2\u00B3\u00B5\-\.\u00B0\w\u00B5\u00B2\u00B3]+)\s*{regex.escape(vs)}"
            m = regex.search(pattern_before, text)
            if m:
                return m.group('unit').strip()

            # Try looser numeric matching (value may appear formatted differently)
            # capture a number near a unit token
            loose = regex.search(r"(?P<num>-?\d+[\.,]?\d*)\s*(?P<unit>[%°μµA-Za-z/\u00B2\u00B3\-]+)", text)
            if loose:
                # prefer matches where numeric equals our value when normalized
                num = _normalize_number_str(loose.group('num'))
                if num == vs:
                    return _normalize_unit_str(loose.group('unit').strip())
                # otherwise still return the unit as a best guess
                return _normalize_unit_str(loose.group('unit').strip())

            return None

        def _fill_units_in_output(parsed, paragraph_text):
            # parsed can be dict (mapping prop->list) or list of dicts
            def _maybe_convert_percent(item, unit):
                # If unit is percent-like and the value is a fraction (0<x<1),
                # convert value to percent string by multiplying by 100.
                try:
                    if unit == '%':
                        v = item.get('value', '')
                        vf = float(str(v).replace(',', '.'))
                        if 0 < vf <= 1:
                            newv = round(vf * 100, 6)
                            # Remove trailing .0
                            if float(int(newv)) == newv:
                                newv = int(newv)
                            item['value'] = str(newv)
                except Exception:
                    pass

            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict) and 'unit' in item and (not item.get('unit')):
                                unit = _infer_unit_from_text(item.get('value', ''), paragraph_text)
                                if unit:
                                    # normalize common unit spellings
                                    unit = _normalize_unit_str(unit)
                                    item['unit'] = unit
                                    _maybe_convert_percent(item, unit)
            elif isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and 'unit' in item and (not item.get('unit')):
                        unit = _infer_unit_from_text(item.get('value', ''), paragraph_text)
                        if unit:
                            unit = _normalize_unit_str(unit)
                            item['unit'] = unit
                            _maybe_convert_percent(item, unit)

        def _normalize_unit_str(u: str) -> str:
            # Normalize common unicode and formatting variants to canonical units
            
            if not u:
                return u
            s = u.replace('\u00A0', ' ')  # no-break space
            s = s.replace('\u2013', '-')
            s = s.replace('\u2212', '-')
            s = s.replace('\u00B9', '1')
            s = s.replace('\u00B2', '2')
            s = s.replace('\u00B3', '3')
            s = s.replace('\u00B5', 'u')
            s = s.replace('µ', 'u')
            s = s.replace('μ', 'u')
            s = s.replace('·', '/')
            s = s.replace('g−1', 'g-1')
            # common pattern: 'mAh g-1' -> 'mAh/g'
            s = regex.sub(r"\s+g[-−]?1", "/g", s)
            s = s.replace('g-1', '/g')
            s = s.replace('mAh/g', 'mAh/g')
            s = s.strip()
            # collapse multiple spaces
            s = regex.sub(r"\s+", " ", s)
            return s

        try:
            _fill_units_in_output(st_output, paragraph)
        except Exception as e:
            # Don't fail the pipeline for unit-inference errors; log them
            print(f"[Property Mining] unit inference error: {e}")

        self._write_log(f"{st_output}", None)

        element.set_data([st_output])
        return {"output": st_output}
    

    def _add_explanation(self,) -> str:
        erase_list = [
            "cell_volume",
            "conversion",
            "reaction_yield",
            "chemical_formula",
        ]
        
        # Use PropertiesOnlyFormatter if properties_only mode is enabled
        if self.properties_only:
            formatter = PropertiesOnlyFormatter
            target_items = list(formatter.explanation.keys())
            # Remove meta from target items as it's not a property to extract
            target_items = [item for item in target_items if item != "meta"]
        else:
            formatter = Formatter
            target_items = list(formatter.explanation.keys())
            target_items = [item for item in target_items if item not in erase_list]
            
        explained_props = ""
        for item in target_items:
            explained_props += "\n" + f"- {item}: " + formatter.explanation[item].strip()
        return explained_props.strip()




    @classmethod
    def from_llm(
        cls,
        type_llm: BaseLanguageModel,
        extract_llm: BaseLanguageModel,
        *,
        prompt_type: str = PROMPT_TYPE,
        prompt_extract: str = PROMPT_EXT,
        ft_type: str = FT_TYPE,
        ft_human: str = FT_HUMAN,
        properties_only: bool = False,
        **kwargs,
    ) -> Runnable:
        
        # Try to use local model for property type classification if available
        local_property_type = LocalModelFactory.get_text_property_type()
        
        if local_property_type and type_llm.model_name != "local-flan-t5-classifier":
            print("Using local FLAN-T5 property type classifier model")
            # For local models, we don't need prompts since they're fine-tuned
            # The local model wrapper handles the prompt internally
            prompt_template = PromptTemplate(template="classify paragraph: {paragraph}", input_variables=["paragraph"])
            type_chain = prompt_template | local_property_type | StrOutputParser()
        elif type_llm.model_name.startswith('ft:'): # fine-tuned model
            system_prompt = SystemMessagePromptTemplate.from_template(ft_type)
            human_prompt = HumanMessagePromptTemplate.from_template(ft_human)
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_prompt, human_prompt]
            )
            type_chain = chat_prompt | type_llm | StrOutputParser()
        else:
            template_type = PromptTemplate(
                template=prompt_type,
                input_variables=["explanation", "paragraph"],
            )
            type_chain = template_type | type_llm | StrOutputParser()

        if extract_llm.model_name.startswith('ft:'): # fine-tuned model
            # Support fine-tuned models for extraction by constructing a
            # chat-style prompt: the system message contains the extraction
            # instructions (PROMPT_EXT) and the human message supplies the
            # per-call variables. This mirrors the `type_llm` fine-tuned
            # handling above.
            system_prompt = SystemMessagePromptTemplate.from_template(prompt_extract)
            # Human prompt includes all variables the system prompt expects.
            human_template = (
                "Prop: {prop}\n"
                "Structured: {structured_data}\n"
                "Info: {information}\n"
                "Example: {example}\n\n"
                "Paragraph: {paragraph}\n"
                "JSON:"
            )
            human_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
            extract_chain = chat_prompt | extract_llm | StrOutputParser()
        else:
            template_extract = PromptTemplate(
                template=prompt_extract,
                input_variables=["prop", "structured_data", "information", "example", "paragraph"],
            )
            extract_chain = template_extract | extract_llm | StrOutputParser()


        return cls(
            type_chain=type_chain,
            extract_chain=extract_chain,
            properties_only=properties_only
        )
    
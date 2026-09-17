# LLM-Text: Large Language Model Text Property Miner

## Summary
LLM-Text is a specialized version of L2M3 designed to extract only property information from text in scientific literature, focusing on battery data. It utilizes Large Language Models (LLMs) to identify and extract property-related information from text paragraphs.

## Process

LLM-Text employs two specialized agents:

- **Categorization Agent**: Classifies text paragraphs to identify those containing property information.
- **Property Extraction Agent**: Extracts property data in a structured JSON format from categorized text.

## Installation

**Requirements**: Python >= 3.9

```bash
$ git clone <repository-url>
$ cd LLM-text
$ pip install -e .
```

## How to use

You can run LLM-Text using the `LLMMiner` and `JournalReader` classes.

```python
from llm_miner import LLMMiner
from llm_miner import JournalReader

# Load agent and parse XML/HTML file
agent = LLMMiner.from_config(config)
jr = JournalReader.from_file(file_path, publisher)

# Run the agent on the parsed file
agent.run(jr)
```

### 1. JournalReader (Parsing XML/HTML)
Same as L2M3, extracts clean text and metadata from XML or HTML files.

### 2. LLMMiner (Agent)
LLMMiner extracts property information from text.

```python
from llm_miner import LLMMiner

api_key = 'openai-api-key'
agent = LLMMiner.create(openai_api_key=api_key)
```

By default, uses `gpt-4` for extraction and `gpt-3.5-turbo-16k` for categorization.

### 3. Run agent
```python
agent.run(jr)
```

Results are consolidated by material.

```python
result = jr.result
result.print()
```

## Fine-tuning
Supports fine-tuning for text categorization and property extraction using datasets in the original L2M3 finetune directory.

## Citation
Based on L2M3: Harnessing Large Language Model to collect and analyze Metal-organic framework property dataset, J. Am. Chem. Soc. 2025, 147, 5, 3943-3958

## License
MIT License

### MatProGPT: Achieving Near-Perfect Fidelity in Materials Property Extraction via Multi-Modal LLMs and Dynamic Prompt Engineering


![Uploading image.png…]()



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
 

## License
MIT License

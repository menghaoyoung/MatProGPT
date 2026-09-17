 


from llm_miner import LLMMiner
from llm_miner.reader import JournalReader
import os

# Configure proxy
os.environ['http_proxy'] = 'http://127.0.0.1:10809'
os.environ['https_proxy'] = 'http://127.0.0.1:10809'

#  API configuration
# CONFIG = {
#     'api_base': 'https://tbnx.plus7.plus/v1',
#     'api_key': 'sk-VUh0cVQe6Jbtl0OND3LfghynsQFcYeEZP2snb0RwIsDm2lwb',
# }

api_key: "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"

# Set XML folder path
xml_folder = "elsevier_xml"

print("Creating LLM Miner agent...")
print("Checking local model configuration...")

# Create agent
agent = LLMMiner.create(openai_api_key=CONFIG['api_key'])

print("Agent created successfully!")
print(f"Processing XML files from: {xml_folder}")

# Process all parsed XML files
if os.path.exists(xml_folder):
    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            file_path = os.path.join(xml_folder, filename)
            
            print(f"\n=== Processing {filename} ===")
            
            # Parse and process
            jr = JournalReader.from_file(file_path, publisher='elsevier')
            agent.run(jr)
            
            # View results
            print(f"\n=== Results for {filename} ===")
            if jr.result:
                jr.result.print()
                
            # Save complete results
            output_json = f"results_{filename.replace('.xml', '.json')}"
            jr.to_json(output_json)
            print(f"Results saved to: {output_json}")
else:
    print(f"XML folder '{xml_folder}' not found!")

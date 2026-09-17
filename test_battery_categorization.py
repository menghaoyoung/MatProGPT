#!/usr/bin/env python3
"""
Test script for battery paper categorization using local models
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.append('/home/ait/Desktop/LLM-projet/L2M3/Transformer_LLM')

from llm_miner.config import config
from llm_miner.local_model_factory import LocalModelFactory
from llm_miner.categorize.base import CategorizeAgent
from llm_miner.reader import JournalReader
from llm_miner.schema import Paragraph

def test_local_model_loading():
    """Test if local models can be loaded successfully"""
    print("="*80)
    print("TESTING LOCAL MODEL LOADING")
    print("="*80)
    
    # Print current config
    print(f"Current config:")
    print(f"  use_local_models: {config.get('use_local_models', False)}")
    print(f"  local_models: {config.get('local_models', {})}")
    
    # Test local model factory
    print("\nTesting LocalModelFactory...")
    factory_info = LocalModelFactory.get_model_info()
    print(f"Factory info: {factory_info}")
    
    # Test text categorizer
    print("\nTesting text categorizer...")
    categorizer = LocalModelFactory.get_text_categorizer()
    
    if categorizer:
        print("✓ Text categorizer loaded successfully")
        return True
    else:
        print("✗ Text categorizer failed to load")
        return False

def test_categorize_agent_creation():
    """Test if CategorizeAgent can be created with local models"""
    print("\n" + "="*80)
    print("TESTING CATEGORIZE AGENT CREATION")
    print("="*80)
    
    try:
        # Create a mock LLM (won't be used if local model is available)
        from langchain_openai import ChatOpenAI
        simple_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
        
        # Try to create categorize agent
        categorize_agent = CategorizeAgent.from_llm(
            llm=simple_llm,
            verbose=True
        )
        
        print("✓ CategorizeAgent created successfully")
        print(f"  Categorize chain type: {type(categorize_agent.categorize_chain)}")
        
        return categorize_agent
    except Exception as e:
        print(f"✗ Failed to create CategorizeAgent: {e}")
        return None

def test_paragraph_classification(categorize_agent):
    """Test classifying actual paragraphs"""
    print("\n" + "="*80)
    print("TESTING PARAGRAPH CLASSIFICATION")
    print("="*80)
    
    # Test paragraphs
    test_paragraphs = [
        {
            "text": "The capacity degradation behavior of lithium-ion batteries subjected to high-rate charge/discharge cycling is depicted in Figure 1. The results indicate a pronounced decline in battery capacity as the charge and discharge cycle numbers increase.",
            "expected": "battery"
        },
        {
            "text": "In this study, we synthesized novel cathode materials for lithium battery applications. The electrochemical performance showed improved capacity retention over 1000 cycles.",
            "expected": "battery"
        },
        {
            "text": "The experimental results demonstrate significant improvements in battery performance compared to conventional materials.",
            "expected": "battery"
        },
        {
            "text": "The Fourier transform infrared spectroscopy (FTIR) analysis confirmed the successful formation of the target compound.",
            "expected": "non battery"
        },
        {
            "text": "Thermal analysis was performed using differential scanning calorimetry to study the thermal stability of the materials.",
            "expected": "non battery"
        }
    ]
    
    if not categorize_agent:
        print("✗ No categorize agent available for testing")
        return False
    
    results = []
    for i, test_case in enumerate(test_paragraphs):
        print(f"\nTesting paragraph {i+1}:")
        print(f"  Text: {test_case['text'][:100]}...")
        print(f"  Expected: {test_case['expected']}")
        
        try:
            # Create a paragraph object
            para = Paragraph(
                content=test_case['text'],
                idx=i,
                type="text"
            )
            
            # Classify
            result = categorize_agent._call({"paragraph": para})
            predicted = result.get('output', [])
            
            print(f"  Predicted: {predicted}")
            
            # Check if prediction matches expected
            is_correct = any(exp.lower() in [p.lower() for p in predicted] 
                           for exp in [test_case['expected']])
            
            print(f"  Result: {'✓ Correct' if is_correct else '✗ Incorrect'}")
            
            results.append({
                "paragraph_id": i+1,
                "text": test_case['text'],
                "expected": test_case['expected'],
                "predicted": predicted,
                "correct": is_correct
            })
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "paragraph_id": i+1,
                "text": test_case['text'],
                "expected": test_case['expected'],
                "predicted": [],
                "correct": False,
                "error": str(e)
            })
    
    # Print summary
    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = correct_count / total_count * 100 if total_count > 0 else 0
    
    print(f"Accuracy: {correct_count}/{total_count} ({accuracy:.1f}%)")
    
    # Save results
    results_file = "battery_classification_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    
    return accuracy > 60  # Consider 60% accuracy as success

def test_file_processing():
    """Test processing an actual XML file if available"""
    print("\n" + "="*80)
    print("TESTING FILE PROCESSING")
    print("="*80)
    
    # Look for XML files
    xml_dirs = [
        "elsevier_xml",
        "XML_to_text1/input_xml"
    ]
    
    xml_files = []
    for xml_dir in xml_dirs:
        xml_path = Path(xml_dir)
        if xml_path.exists():
            xml_files.extend(xml_path.glob("*.xml"))
    
    if not xml_files:
        print("No XML files found for testing")
        return False
    
    xml_file = xml_files[0]
    print(f"Testing with file: {xml_file}")
    
    try:
        # Create JournalReader
        jr = JournalReader.from_file(str(xml_file), publisher="elsevier")
        print(f"✓ JournalReader created")
        print(f"  DOI: {jr.doi}")
        print(f"  Title: {jr.title}")
        print(f"  Elements count: {len(jr.elements)}")
        
        # Test categorization
        categorize_agent = test_categorize_agent_creation()
        if categorize_agent:
            for element in jr.elements:
                try:
                    result = categorize_agent.invoke({"paragraph": element})
                    print(f"  Element {element.idx}: {result.get('output', [])}")
                except Exception as e:
                    print(f"  Element {element.idx}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ File processing failed: {e}")
        return False

def main():
    """Main test function"""
    print("BATTERY PAPER CATEGORIZATION TEST")
    print("="*80)
    
    # Test 1: Local model loading
    models_loaded = test_local_model_loading()
    
    if not models_loaded:
        print("\n⚠️  Local models not loaded. Check configuration.")
        print("Make sure the model paths exist and use_local_models is True.")
        return
    
    # Test 2: Categorize agent creation
    categorize_agent = test_categorize_agent_creation()
    
    # Test 3: Paragraph classification
    if categorize_agent:
        accuracy = test_paragraph_classification(categorize_agent)
        
        if accuracy:
            print("\n✓ Battery paper categorization is working correctly!")
        else:
            print("\n⚠️  Classification accuracy is low. Check model performance.")
    
    # Test 4: File processing (optional)
    test_file_processing()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

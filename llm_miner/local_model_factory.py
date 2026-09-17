#!/usr/bin/env python3
"""
Local Model Factory for LLM Miner
This module provides centralized access to local fine-tuned models
"""

import os
from typing import Optional, Any
from llm_miner.config import config

# Import the local model wrapper
try:
    from finetune.text_classification_model.local_model_wrapper import LocalFLANT5Model
except ImportError:
    # Handle case where the module is not in the path
    import sys
    import pathlib
    current_dir = pathlib.Path(__file__).parent
    sys.path.append(str(current_dir / ".." / "finetune" / "text_classification_model"))
    from local_model_wrapper import LocalFLANT5Model


class LocalModelFactory:
    """
    Factory class for managing local models
    """
    
    _models = {}
    
    @classmethod
    def get_text_categorizer(cls) -> Optional[Any]:
        """
        Get or create the text classification model
        """
        model_key = "text_categorizer"
        
        if model_key not in cls._models:
            # Check if local models are enabled
            if not config.get("use_local_models", False):
                return None
            
            # Get the model path from config
            model_path = config.get("local_models", {}).get("local_text_categorize")
            
            if not model_path or model_path is None:
                print("No local text categorizer model configured")
                return None
            
            # Check if model path exists
            if not os.path.exists(model_path):
                print(f"Local model path does not exist: {model_path}")
                return None
            
            try:
                print(f"Loading local text categorizer from: {model_path}")
                cls._models[model_key] = LocalFLANT5Model(model_path=model_path)
                print("✓ Local text categorizer loaded successfully")
            except Exception as e:
                print(f"Failed to load local text categorizer: {e}")
                return None
        
        return cls._models.get(model_key)
    
    @classmethod
    def get_text_property_type(cls) -> Optional[Any]:
        """
        Get or create the text property type classification model
        """
        model_key = "text_property_type"
        
        if model_key not in cls._models:
            # Check if local models are enabled
            if not config.get("use_local_models", False):
                return None
            
            # Get the model path from config
            model_path = config.get("local_models", {}).get("local_text_property_type")
            
            if not model_path or model_path is None:
                print("No local text property type model configured")
                return None
            
            # Check if model path exists
            if not os.path.exists(model_path):
                print(f"Local model path does not exist: {model_path}")
                return None
            
            try:
                print(f"Loading local text property type model from: {model_path}")
                cls._models[model_key] = LocalFLANT5Model(model_path=model_path)
                print("✓ Local text property type model loaded successfully")
            except Exception as e:
                print(f"Failed to load local text property type model: {e}")
                return None
        
        return cls._models.get(model_key)
    
    @classmethod
    def get_text_property_extract(cls) -> Optional[Any]:
        """
        Get or create the text property extraction model
        """
        model_key = "text_property_extract"
        
        if model_key not in cls._models:
            # Check if local models are enabled
            if not config.get("use_local_models", False):
                return None
            
            # Get the model path from config
            model_path = config.get("local_models", {}).get("local_text_property_extract")
            
            if not model_path or model_path is None:
                print("No local text property extract model configured")
                return None
            
            # Check if model path exists
            if not os.path.exists(model_path):
                print(f"Local model path does not exist: {model_path}")
                return None
            
            try:
                print(f"Loading local text property extract model from: {model_path}")
                cls._models[model_key] = LocalFLANT5Model(model_path=model_path)
                print("✓ Local text property extract model loaded successfully")
            except Exception as e:
                print(f"Failed to load local text property extract model: {e}")
                return None
        
        return cls._models.get(model_key)
    
    @classmethod
    def clear_models(cls):
        """Clear all loaded models from cache"""
        cls._models.clear()
        print("Cleared all cached local models")
    
    @classmethod
    def get_model_info(cls) -> dict:
        """Get information about loaded models"""
        info = {
            "use_local_models": config.get("use_local_models", False),
            "loaded_models": list(cls._models.keys()),
            "config": {
                "text_categorize": config.get("local_models", {}).get("local_text_categorize"),
                "text_property_type": config.get("local_models", {}).get("local_text_property_type"),
                "text_property_extract": config.get("local_models", {}).get("local_text_property_extract"),
            }
        }
        return info


# Convenience functions
def get_local_text_categorizer():
    """Convenience function to get text categorizer"""
    return LocalModelFactory.get_text_categorizer()


def get_local_text_property_type():
    """Convenience function to get text property type model"""
    return LocalModelFactory.get_text_property_type()


def get_local_text_property_extract():
    """Convenience function to get text property extract model"""
    return LocalModelFactory.get_text_property_extract()


# Test function
def test_local_models():
    """Test function to verify local models are working"""
    print("Testing Local Model Factory")
    print("="*50)
    
    # Print config info
    info = LocalModelFactory.get_model_info()
    print(f"Local models enabled: {info['use_local_models']}")
    print(f"Config: {info['config']}")
    
    # Test text categorizer
    print("\nTesting text categorizer...")
    categorizer = get_local_text_categorizer()
    
    if categorizer:
        test_text = "The capacity of the battery was measured to be 2500 mAh at 1C rate."
        try:
            result = categorizer._call(f"classify paragraph: {test_text}")
            print(f"✓ Text categorizer test passed: {result}")
        except Exception as e:
            print(f"✗ Text categorizer test failed: {e}")
    else:
        print("✗ Text categorizer not available")
    
    # Print final info
    final_info = LocalModelFactory.get_model_info()
    print(f"\nFinal status: {final_info}")


if __name__ == "__main__":
    test_local_models()




config = {
    # default llms
    "model_name": "gpt-4",
    "simple_model_name": "gpt-3.5-turbo-0125",
    
    # Local models (from YAML config)
    "local_models": {
        "local_text_categorize": "./finetune/text_classification_model/flan-t5_finetuning",
        "local_text_property_type": "./finetune/categorize_battery_paper_model/flan-t5_finetuning",
        "local_text_property_extract": None,
    },
    
    # Legacy local_model entries (for backward compatibility)
    "local_model": {
        "categorize_battery_paper": "finetune/categorize_battery_paper_model",
        "paragraph_classification": "finetune/text_classification_model",
    },
    
    # fine-tuned llms (optional)
    "fine_tuning_models": {
        "ft_paper_categorize": "ft:gpt-3.5-turbo-0125:tongji::Cgkl2hu9",
        "ft_text_property_type": "ft:gpt-3.5-turbo-0125:tongji::CZCJ6Vxj",
        "ft_text_property_extract": "ft:gpt-3.5-turbo-0125:tongji::Cg12FEYr",
    },
    
    # llm options
    "temperature": 0.0,
    "verbose": False,
    # Request timeout (seconds) for remote LLM calls.
    "llm_request_timeout": 60,
    
    # config - agent
    "reconstruct": True,
    "input_max_tokens_property": 3500,
    
    # use local models flag
    # use local models flag
    # By default we disable local model loading so the system uses only
    # the configured fine-tuned / remote models. Set this to True only
    # if you explicitly want to enable local finetuned model directories.
    "use_local_models": False,
}

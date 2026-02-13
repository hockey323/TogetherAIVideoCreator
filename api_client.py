
import os
import streamlit as st
from together import Together
from dotenv import load_dotenv
from models import VIDEO_MODEL_REGISTRY, IMAGE_MODEL_REGISTRY

# Load environment variables
load_dotenv()

# Initialize Together client
def get_client():
    try:
        api_key = os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            st.error("TOGETHER_API_KEY not found in environment variables.")
            st.stop()
        return Together(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize Together client: {e}")
        st.stop()

client = get_client()

@st.cache_data(ttl=3600)
def fetch_available_models(model_type='video'):
    """Fetch available models from Together API filtered by type"""
    try:
        models = client.models.list()
        filtered_models = []
        
        # Determine target registry
        registry = VIDEO_MODEL_REGISTRY if model_type == 'video' else IMAGE_MODEL_REGISTRY
        
        for model in models:
            # Check if model type matches or if it's in our registry
            if hasattr(model, 'type') and model.type and model_type.lower() in model.type.lower():
                filtered_models.append(model.id)
            elif model.id in registry:
                filtered_models.append(model.id)
        
        if filtered_models:
            return sorted(list(set(filtered_models)))
        else:
            return sorted(list(registry.keys()))
            
    except Exception as e:
        st.warning(f"Could not fetch {model_type} models from API: {e}. Using default registry.")
        registry = VIDEO_MODEL_REGISTRY if model_type == 'video' else IMAGE_MODEL_REGISTRY
        return sorted(list(registry.keys()))

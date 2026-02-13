
class ModelConfig:
    def __init__(self, 
                 supported_params: set, 
                 defaults: dict = None,
                 transforms: dict = None,
                 key_mapping: dict = None,
                 image_support: bool = False,
                 must_have_image: bool = False):
        self.supported_params = supported_params
        self.defaults = defaults or {}
        self.transforms = transforms or {}
        self.key_mapping = key_mapping or {}
        self.image_support = image_support
        self.must_have_image = must_have_image

    def is_supported(self, param: str) -> bool:
        return param in self.supported_params

    def apply_transforms(self, params: dict) -> dict:
        """Apply key mappings, then value transforms, then filter allowed params"""
        raw_params = params.copy()
        
        # Base parameters that are always allowed
        core_allowed = {"model", "prompt"}
        allowed_keys = core_allowed | self.supported_params
        
        # STEP 1: Apply key mappings first
        mapped_params = {}
        for k, v in raw_params.items():
            dest_key = self.key_mapping.get(k, k)
            mapped_params[dest_key] = v
        
        # STEP 2: Apply value transforms
        for key, transform in self.transforms.items():
            # Check original key
            if key in mapped_params and mapped_params[key] is not None:
                mapped_params[key] = transform(mapped_params[key])
            # Check mapped key
            mapped_key = self.key_mapping.get(key, key)
            if mapped_key != key and mapped_key in mapped_params and mapped_params[mapped_key] is not None:
                mapped_params[mapped_key] = transform(mapped_params[mapped_key])

        # STEP 3: Filter to only allowed parameters
        final_params = {}
        for k, v in mapped_params.items():
            original_key = next((orig for orig, mapped in self.key_mapping.items() if mapped == k), k)
            if k in allowed_keys or original_key in allowed_keys or k in core_allowed:
                final_params[k] = v
                
        return final_params

# Common sets of parameters
STANDARD_DIFFUSION_PARAMS = {
    "width", "height", "fps", "steps", "guidance_scale", "seed", "negative_prompt", "output_format", "seconds", "prompt"
}

VEO_PARAMS = {
    "width", "height", "fps", "seconds", "output_format", "output_quality", "prompt", "negative_prompt", "seed"
}

KLING_PARAMS = {
    "width", "height", "fps", "seconds", "guidance_scale", "seed", "negative_prompt", "output_format", "output_quality", "prompt"
}

KLING_2_1_PARAMS = {
    "width", "height", "seconds", "guidance_scale", "seed", "negative_prompt", "output_format", "output_quality", "prompt"
}

SEEDANCE_PARAMS = {
    "width", "height", "fps", "seconds", "output_format", "output_quality", "prompt", "seed"
}

SORA_PARAMS = {
    "width", "height", "fps", "seconds", "output_format", "output_quality", "prompt"
}

VIDU_PARAMS = {
    "width", "height", "seconds", "seed", "output_format", "output_quality", "prompt"
}

def transform_kling_images(images):
    # Kling expects [{"input_image": "base64..."}, ...]
    return [{"input_image": img} for img in images]

# Video Model Registry
VIDEO_MODEL_REGISTRY = {
    # Minimax
    "minimax/video-01-director": ModelConfig(
        supported_params={"width", "height", "fps", "seconds", "output_format", "output_quality", "prompt", "model"},
        defaults={"fps": 25, "width": 1280, "height": 720, "output_quality": 25, "seconds": 8},
        transforms={"seconds": str}
    ),
    "minimax/hailuo-02": ModelConfig(
        supported_params={"width", "height", "fps", "seconds", "output_format", "output_quality", "prompt"},
        defaults={"seconds": 8},
        image_support=True,
        transforms={"seconds": str}
    ),
    # Google Veo
    "google/veo-2.0": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0-fast": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0-audio": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0-fast-audio": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.1": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    # Kling
    "kwaivgI/kling-2.1-master": ModelConfig(
        supported_params=KLING_2_1_PARAMS, 
        defaults={"seconds": 5},
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),
    "kwaivgI/kling-2.1-pro": ModelConfig(
        supported_params=KLING_2_1_PARAMS, 
        defaults={"seconds": 5},
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True,
        must_have_image=True
    ),
    "kwaivgI/kling-2.1-standard": ModelConfig(
        supported_params=KLING_2_1_PARAMS, 
        defaults={"seconds": 5},
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True,
        must_have_image=True
    ),
    "kwaivgI/kling-2.0-master": ModelConfig(
        supported_params=KLING_PARAMS, 
        defaults={"seconds": 5}, 
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),
    "kwaivgI/kling-1.6-pro": ModelConfig(
        supported_params=KLING_PARAMS, 
        defaults={"seconds": 5}, 
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),
    "kwaivgI/kling-1.6-standard": ModelConfig(
        supported_params=KLING_PARAMS, 
        defaults={"seconds": 5}, 
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),
    # Seedance
    "ByteDance/Seedance-1.0-pro": ModelConfig(supported_params=SEEDANCE_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),
    "ByteDance/Seedance-1.0-lite": ModelConfig(supported_params=SEEDANCE_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),
    # Wan
    "Wan-AI/Wan2.2-T2V-A14B": ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),
    "Wan-AI/Wan2.2-I2V-A14B": ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),
    # PixVerse
    "pixverse/pixverse-v5": ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}),
    # Sora
    "openai/sora-2-pro": ModelConfig(supported_params=SORA_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}),
    "openai/sora-2": ModelConfig(supported_params=SORA_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}),
    # Vidu
    "vidu/vidu-2.0": ModelConfig(
        supported_params=VIDU_PARAMS, 
        defaults={"seconds": 8}, 
        image_support=True, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        key_mapping={"reference_images": "frame_images"}, 
        must_have_image=True
    ),
    "vidu/vidu-q1": ModelConfig(
        supported_params=VIDU_PARAMS, 
        defaults={"seconds": 8}, 
        image_support=True, 
        transforms={"seconds": str, "reference_images": transform_kling_images},
        key_mapping={"reference_images": "frame_images"},
        must_have_image=True
    ),
}

# Image Model Registry (New)
IMAGE_MODEL_REGISTRY = {
    "black-forest-labs/FLUX.1-schnell": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 768, "steps": 4},
        image_support=True,
        key_mapping={"reference_images": "image"},
        transforms={"reference_images": lambda x: x[0] if isinstance(x, list) and x else x}
    ),
    "black-forest-labs/FLUX.1-dev": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "guidance_scale", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 768, "steps": 28, "guidance_scale": 3.5},
        image_support=True,
        key_mapping={"reference_images": "image"},
        transforms={"reference_images": lambda x: x[0] if isinstance(x, list) and x else x}
    ),
    "google/gemini-2.5-flash-image": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 768, "steps": 20},
        image_support=True
    ),
    "google/gemini-3-pro-image-preview": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 768, "steps": 20},
        image_support=True
    ),
    "NanoBanana/NanoBanana-v1": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 768, "steps": 20},
        image_support=True
    ),
    "google/flash-image-2.5": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 768, "steps": 20},
        image_support=True
    ),
    "google/imagen-3.0": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 1024, "steps": 20},
        image_support=True
    ),
    "google/imagen-4.0-preview": ModelConfig(
        supported_params={"width", "height", "steps", "seed", "prompt", "reference_images"},
        defaults={"width": 1024, "height": 1024, "steps": 20},
        image_support=True
    ),
}

DEFAULT_VIDEO_CONFIG = ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS)
DEFAULT_IMAGE_CONFIG = ModelConfig(supported_params={"width", "height", "steps", "seed", "prompt"})

def get_video_model_config(model_name: str) -> ModelConfig:
    return VIDEO_MODEL_REGISTRY.get(model_name, DEFAULT_VIDEO_CONFIG)

def get_image_model_config(model_name: str) -> ModelConfig:
    # Try exact match first
    if model_name in IMAGE_MODEL_REGISTRY:
        return IMAGE_MODEL_REGISTRY[model_name]
    
    # Try fuzzy match (if model name contains registry key or vice versa)
    for key, config in IMAGE_MODEL_REGISTRY.items():
        if key in model_name or model_id_clean(key) in model_id_clean(model_name):
            return config
            
    return DEFAULT_IMAGE_CONFIG

def model_id_clean(model_id: str) -> str:
    return model_id.lower().split('/')[-1]

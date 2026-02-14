# Together AI Studio

A Streamlit-based application for generating **videos** and **images** using [Together AI](https://www.together.ai/) serverless models. Features a modern dark-themed UI with support for 30+ models from Google, OpenAI, Kling, ByteDance, and more.

## Features

- **🎬 Video Studio** — Generate videos with models like Veo 3.1, Sora 2, Kling 2.1, Seedance, and more
- **🎨 Image Studio** — Generate images with FLUX, Gemini, Imagen, NanoBanana, and others
- **🖼️ Image-to-Video / Image-to-Image** — Use a reference image as input for supported models
- **⚙️ Dynamic Parameters** — UI adjusts automatically based on each model's supported parameters
- **💾 Auto-Save** — Optionally save generated media to a local directory
- **📋 Job Queue** — Track and retrieve long-running video generation jobs

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/hockey323/TogetherAIVideoCreator.git
cd TogetherAIVideoCreator
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example file and add your API key:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your_api_key_here` with your [Together AI API key](https://api.together.ai/):

```
TOGETHER_API_KEY=your_actual_key_here
```

### 5. Run the App

```bash
streamlit run app.py
```

## Configuration

All configuration is done via the `.env` file:

| Variable | Required | Description |
|---|---|---|
| `TOGETHER_API_KEY` | ✅ Yes | Your Together AI API key |
| `VIDEO_OUTPUT_PATH` | No | Directory to auto-save generated videos |
| `IMAGE_OUTPUT_PATH` | No | Directory to auto-save generated images |

## Supported Models

### Video Models
Google Veo (2.0, 3.0, 3.1), OpenAI Sora 2, Kling (1.6–2.1), ByteDance Seedance, Minimax, Wan-AI, PixVerse, Vidu, and more.

### Image Models
FLUX.1 (Schnell, Dev), Google Gemini, Imagen (3.0, 4.0), NanoBanana, and more.

## Notes

- Generated media is hosted temporarily by Together AI — use the download button or auto-save to keep your files.
- See the [Together AI Documentation](https://docs.together.ai/docs/serverless-models) for details on model parameters and pricing.

## License

MIT

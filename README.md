
# Together AI Video Generator

This project allows you to generate videos using Together AI's serverless models through a beautiful Streamlit interface.

## Setup

1.  **Install Dependencies**: A virtual environment has been created and dependencies installed.
    If you need to reinstall:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

2.  **API Key**: The API key is configured in the `.env` file. Refrain from sharing this file if you push to a public repository.

## Running the App

To start the video generator, simply run the `run.ps1` script in PowerShell:

```powershell
.\run.ps1
```

Or manually:

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

## Features

-   **Model Selection**: Choose from various video models like `minimax/video-01-director`, `google/veo-2.0`, and more.
-   **Custom Parameters**: Adjust resolution, FPS, steps, and guidance scale.
-   **Modern UI**: Dark-themed interface with custom styling.
-   **Download**: Direct download link for generated videos.

## Auto-Save

The application can automatically save generated images and videos to your local machine. This is configured via environment variables in the `.env` file:

-   `VIDEO_OUTPUT_PATH`: Directory where generated videos will be saved (e.g., `D:\Videos\TogetherAI`).
-   `IMAGE_OUTPUT_PATH`: Directory where generated images will be saved (e.g., `D:\Images\TogetherAI`).

If these variables are not set, the application will not automatically save the files.

## Notes

-   The generated videos and images are hosted by Together AI temporarily. Download them or use auto-save if you wish to keep them.
-   Check the [Together AI Documentation](https://docs.together.ai/docs/serverless-models#video-models) for meaningful parameter ranges for specific models.

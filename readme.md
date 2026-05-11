# Runway API Hackathon

A batch RunwayML image generation and upscaling workflow pipeline built with `n8n` and `Modal`.

## Project Overview

- `n8n_runwayml_workflow.json` — workflow definition for generating prompts, submitting RunwayML image generation jobs, downloading media, and triggering an image upscaler.
- `modal_image_upscaler.py` — Modal application that upscales images from Cloudflare R2 and writes results back to R2.

## Key Features

- Prompt generation via a LangChain-style node
- RunwayML text-to-image request with API key placeholder
- Download of generated media URLs
- Modal-powered R2 image upscaling pipeline
- Example placeholder configuration for secrets and credentials

## Setup

1. Clone the repository.
2. Install Python dependencies if using `modal_image_upscaler.py` locally:

```bash
python -m pip install modal boto3 tqdm opencv-python fastapi
```

3. Configure credentials using environment variables or secret manager.
4. Deploy and execute the setups. See more at [this YouTube walkthrough](https://www.youtube.com/watch?v=YauKJraKOWM).

### Required placeholders

- `YOUR_RUNWAY_API_KEY`, `https://YOUR_MODAL_DEPLOYMENT_URL.modal.run` in `n8n_runwayml_workflow.json` (editable in the JSON or via the n8n workflow UI)
- `YOUR_R2_ENDPOINT`, `YOUR_R2_ACCESS_KEY`, `YOUR_R2_SECRET_KEY` in `modal_image_upscaler.py`

## Usage

1. Import `n8n_runwayml_workflow.json` into `n8n`.
2. Replace the placeholder Runway API key, and all relevant secrets/credentials with your own secret.
3. Deploy or run the Modal app and ensure the R2 bucket configuration is correct.
4. Trigger the workflow to generate images and run the upscale process.

## Notes

- The repo intentionally keeps secrets as placeholders.
- Do not commit real API keys or credentials.
- Happy customize and tinkering!

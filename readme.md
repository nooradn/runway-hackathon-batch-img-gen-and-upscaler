# Runway API Hackathon

A lightweight RunwayML image generation and upscaling pipeline built with `n8n` and `Modal`.

![Architecture infographic](docs/architecture-placeholder.png)

> Replace the placeholder image with an actual diagram showing the flow from prompt generation, RunwayML API request, media download, and Modal R2 upscaling.

## Project Overview

- `n8n_runwayml_workflow.json` — workflow definition for generating prompts, submitting RunwayML image generation jobs, downloading media, and triggering an image upscaler.
- `modal_image_upscaler.py` — Modal application that upscales images from Cloudflare R2 and writes results back to R2.
- `src/images/` — image assets or generated test content.

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

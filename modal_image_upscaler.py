import modal
import os
import subprocess
import shutil
import glob

# --- CONFIG ---
# You can store it in Modal's secret manager too 
# Note: Cloudflare R2 is S3-compatible, so we can use boto3 with custom endpoint and signature config
R2_ENDPOINT = "YOUR_R2_ENDPOINT"  # e.g. https://<account_id>.r2.cloudflarestorage.com
R2_ACCESS_KEY = "YOUR_R2_ACCESS_KEY"
R2_SECRET_KEY = "YOUR_R2_SECRET_KEY"
BUCKET_NAME = "playground" # Your R2 bucket name
INPUT_PREFIX = "input/"
OUTPUT_PREFIX = "output/"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
WEIGHTS_DIR = "/root/weights"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "wget", "git", "libgl1-mesa-glx", "libglib2.0-0")
    .pip_install(
        "torch==2.1.2",
        "torchvision==0.16.2",
        extra_options="--extra-index-url https://download.pytorch.org/whl/cu118",
    )
    .pip_install("boto3", "tqdm", "opencv-python", "fastapi[standard]")
    .run_commands(
        "pip install setuptools==69.5.1",
        "pip install git+https://github.com/xinntao/BasicSR.git --no-build-isolation",
        "pip install realesrgan --no-deps",
    )
    .run_commands("pip install 'numpy<2' --force-reinstall")
    .run_commands(
        "wget https://raw.githubusercontent.com/xinntao/Real-ESRGAN/master/inference_realesrgan.py -O /root/inference_realesrgan.py",
        f"mkdir -p {WEIGHTS_DIR} && wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P {WEIGHTS_DIR}/",
    )
)

app = modal.App("r2-image-upscaler-only-runway-hackathon")

def make_r2_client():
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )

# ---------------------------------------------------------------------------
# WORKER: Process -> Upload (Same Name) -> Delete Input
# ---------------------------------------------------------------------------
@app.function(
    image=image,
    gpu="T4", 
    timeout=600, 
    cpu=2.0,
    memory=4096,
)
def upscale_image_worker(filename: str) -> dict:
    r2 = make_r2_client()
    
    input_key = f"{INPUT_PREFIX}{filename}"
    local_in = f"/tmp/{filename}"
    local_out_dir = "/tmp/outputs"
    
    if os.path.exists(local_out_dir):
        shutil.rmtree(local_out_dir)
    os.makedirs(local_out_dir, exist_ok=True)

    try:
        print(f"[↓] Downloading: {filename}")
        r2.download_file(BUCKET_NAME, input_key, local_in)

        print(f"[⚙] Processing: {filename}")
        subprocess.run(
            [
                "python3", "/root/inference_realesrgan.py",
                "-n", "RealESRGAN_x4plus",
                "-i", local_in,
                "-o", local_out_dir,
                "-s", "4",
                "--fp32",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        # Cari file hasil (biasanya nambahin suffix _out di disk lokal)
        produced = glob.glob(os.path.join(local_out_dir, "*"))
        if not produced:
            raise FileNotFoundError("Upscale failed.")

        local_output_path = produced[0]
        # Kita pakai ORIGINAL filename untuk key di R2 (Tanpa suffix _out)
        output_key = f"{OUTPUT_PREFIX}{filename}"

        print(f"[↑] Uploading high-res asset: {filename}")
        r2.upload_file(local_output_path, BUCKET_NAME, output_key)

        # Misi Sukses? Hapus file original di folder input R2
        print(f"[✂] Cleaning up original input: {filename}")
        r2.delete_object(Bucket=BUCKET_NAME, Key=input_key)

        return {"status": "ok", "file": filename}

    except Exception as e:
        print(f"[✗] Error during mission {filename}: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        if os.path.exists(local_in): os.remove(local_in)
        if os.path.exists(local_out_dir): shutil.rmtree(local_out_dir)

# ---------------------------------------------------------------------------
# TRIGGER
# ---------------------------------------------------------------------------
@app.function(image=image, timeout=300)
@modal.fastapi_endpoint(method="GET")
def execute_trigger():
    r2 = make_r2_client()
    
    print(f"[🔍] Scanning for new targets...")
    resp = r2.list_objects_v2(Bucket=BUCKET_NAME, Prefix=INPUT_PREFIX)
    
    files = [
        obj["Key"].removeprefix(INPUT_PREFIX)
        for obj in resp.get("Contents", [])
        if obj["Key"] != INPUT_PREFIX and obj["Key"].lower().endswith(IMAGE_EXTENSIONS)
    ]

    if not files:
        return {"status": "ignored", "message": "Input folder is clean, Sensei."}

    print(f"[🚀] Found {len(files)} new targets. Deploying workers...")
    for f in files:
        upscale_image_worker.spawn(f)

    return {
        "status": "success",
        "targets_acquired": len(files),
        "files": files
    }

@app.local_entrypoint()
def main():
    execute_trigger.remote()
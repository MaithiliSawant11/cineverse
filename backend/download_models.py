"""
Build-time script to ensure model files are actual binary artifacts (not Git LFS pointers)
and verify their sizes before starting the application.
"""

import os
import sys
import urllib.request

MODELS = {
    "similarity.pkl": {
        "min_mb": 10.0,
        "expected_min_mb": 170.0,
        "expected_max_mb": 195.0,
        "url": "https://media.githubusercontent.com/media/MaithiliSawant11/cineverse/main/backend/models/similarity.pkl",
    },
    "movie_list.pkl": {
        "min_mb": 1.0,
        "expected_min_mb": 1.5,
        "expected_max_mb": 3.0,
        "url": "https://media.githubusercontent.com/media/MaithiliSawant11/cineverse/main/backend/models/movie_list.pkl",
    },
    "count_vectorizer.pkl": {
        "min_mb": 0.05,
        "expected_min_mb": 0.08,
        "expected_max_mb": 0.3,
        "url": "https://media.githubusercontent.com/media/MaithiliSawant11/cineverse/main/backend/models/count_vectorizer.pkl",
    },
}

def verify_and_download(models_dir: str = "models"):
    print(f"==> Verifying model artifacts in '{models_dir}'...")
    os.makedirs(models_dir, exist_ok=True)
    
    for filename, config in MODELS.items():
        filepath = os.path.join(models_dir, filename)
        current_size_mb = 0.0
        if os.path.exists(filepath):
            current_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            
        # Check if actual file is missing or is just a Git LFS pointer file (~130 bytes)
        if current_size_mb < config["min_mb"]:
            print(f"[!] {filename} is only {current_size_mb:.4f} MB (Git LFS pointer detected).")
            print(f"    Downloading actual binary asset from {config['url']} ...")
            req = urllib.request.Request(
                config["url"],
                headers={"User-Agent": "CineverseDockerBuild/1.0"}
            )
            try:
                with urllib.request.urlopen(req) as resp, open(filepath, "wb") as f:
                    downloaded = 0
                    while chunk := resp.read(1024 * 1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (20 * 1024 * 1024) == 0:
                            print(f"    Downloaded {downloaded / (1024 * 1024):.1f} MB ...")
                current_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"    Successfully downloaded {filename}: {current_size_mb:.2f} MB")
            except Exception as e:
                print(f"ERROR: Failed to download {filename} from {config['url']}: {e}", file=sys.stderr)
                sys.exit(1)

        # Build-time size validation
        if not (config["expected_min_mb"] <= current_size_mb <= config["expected_max_mb"]):
            print(
                f"ERROR: {filename} size is {current_size_mb:.2f} MB, which is outside the expected range "
                f"[{config['expected_min_mb']} MB - {config['expected_max_mb']} MB]!",
                file=sys.stderr,
            )
            sys.exit(1)
            
        print(f"  [OK] {filename}: {current_size_mb:.2f} MB (within valid range)")

    print("==> All model artifacts verified successfully! [OK]")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "models"
    verify_and_download(target_dir)

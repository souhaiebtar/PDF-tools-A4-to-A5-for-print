import io
import json
import os
import shutil
import urllib.request
import zipfile

# Common HTTP headers for GitHub API requests
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_latest_release_info(repo):
    """Fetch latest release metadata from GitHub API."""
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(api_url, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def find_asset_url(assets, pattern):
    """Find download URL for an asset matching the given pattern."""
    for asset in assets:
        if pattern in asset["name"]:
            return asset["browser_download_url"]
    return None


def download_zip(url):
    """Download a zip file and return its contents as bytes."""
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(req) as response:
        return response.read()


def download_pdfcpu(target_dir):
    """Download pdfcpu.exe from GitHub releases if not already present."""
    exe_path = os.path.join(target_dir, "pdfcpu.exe")
    if os.path.exists(exe_path):
        print("pdfcpu.exe already exists, skipping download.")
        return

    print("Fetching latest pdfcpu release info...")
    try:
        data = get_latest_release_info("pdfcpu/pdfcpu")
        print(f"Latest pdfcpu version: {data['tag_name']}")

        download_url = find_asset_url(data["assets"], "Windows_x86_64.zip")
        if not download_url:
            print("Could not find Windows_x86_64.zip for pdfcpu.")
            return

        print(f"Downloading pdfcpu from: {download_url}")
        zip_data = download_zip(download_url)

        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            exe_in_zip = next(
                (f.filename for f in z.infolist() if f.filename.endswith("pdfcpu.exe")),
                None,
            )
            if not exe_in_zip:
                print("pdfcpu.exe not found in zip.")
                return

            with z.open(exe_in_zip) as source, open(exe_path, "wb") as target:
                shutil.copyfileobj(source, target)

        print("Successfully installed pdfcpu.exe")
    except Exception as e:
        print(f"Error downloading pdfcpu: {e}")


def download_qpdf(target_dir):
    """Download qpdf binaries from GitHub releases if not already present."""
    qpdf_dir = os.path.join(target_dir, "qpdf")
    exe_path = os.path.join(qpdf_dir, "qpdf.exe")
    if os.path.exists(exe_path):
        print("qpdf.exe already exists, skipping download.")
        return

    print("Fetching latest qpdf release info...")
    try:
        data = get_latest_release_info("qpdf/qpdf")
        print(f"Latest qpdf version: {data['tag_name']}")

        download_url = find_asset_url(data["assets"], "msvc64.zip")
        if not download_url:
            print("Could not find msvc64.zip for qpdf.")
            return

        print(f"Downloading qpdf from: {download_url}")
        zip_data = download_zip(download_url)

        if os.path.exists(qpdf_dir):
            shutil.rmtree(qpdf_dir)
        os.makedirs(qpdf_dir)

        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            for file_info in z.infolist():
                if "/bin/" not in file_info.filename or file_info.is_dir():
                    continue

                parts = file_info.filename.split("/")
                bin_index = parts.index("bin")
                relative_path = os.path.join(*parts[bin_index + 1 :])
                dest_path = os.path.join(qpdf_dir, relative_path)

                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with z.open(file_info) as source, open(dest_path, "wb") as target:
                    shutil.copyfileobj(source, target)

        print("Successfully installed qpdf binaries")
    except Exception as e:
        print(f"Error downloading qpdf: {e}")


def main():
    """Download all required dependencies to the script's directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_pdfcpu(base_dir)
    download_qpdf(base_dir)


if __name__ == "__main__":
    main()

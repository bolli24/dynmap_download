import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from typing import List
import glob
import os


def combine_images() -> None:
    image_files: List[str] = glob.glob('output/*_*.jpg')
    x_values: List[int] = [int(os.path.splitext(os.path.basename(image))[
                               0].split('_')[0]) for image in image_files]
    y_values: List[int] = [int(os.path.splitext(os.path.basename(image))[
                               0].split('_')[1]) for image in image_files]
    min_x: int = min(x_values)
    max_x: int = max(x_values)
    min_y: int = min(y_values)
    max_y: int = max(y_values)
    full_image: Image.Image = Image.new(
        'RGB', (128 * (max_x - min_x + 1), 128 * (max_y - min_y + 1)))
    for image_file in image_files:
        x: int = int(os.path.splitext(
            os.path.basename(image_file))[0].split('_')[0])
        y: int = int(os.path.splitext(
            os.path.basename(image_file))[0].split('_')[1])
        image: Image.Image = Image.open(image_file)
        full_image.paste(image, (128 * (x - min_x), 128 * (max_y - y)))
    file_name = get_file_name('full_image', 'png')
    print(f"Saving {file_name}")
    full_image.save(file_name)


def get_file_name(name: str, extension: str, increment=0) -> str:
    if (increment == 0 and os.path.exists(f"{name}.{extension}")) or os.path.exists(f"{name}_{increment}.{extension}"):
        return get_file_name(name, extension, increment + 1)

    return f"{name}_{increment}.{extension}" if increment > 0 else f"{name}.{extension}"


def download_image(url: str, size: int, i: int, j: int, step: int) -> None:
    # http://play.warpedsmp.com:25572/tiles/world/flat/-3_1/zz_-68_44.jpg
    img_url = f"{url}/tiles/world/flat/{0}_{0}/zz_{(-size + i)}_{(-size + j)}.jpg"
    img_path = f"output/{i // step}_{j // step}.jpg"
    if (os.path.exists(img_path)):
        print(f"Skipping {img_url} because {img_path} exists")
        return
    print(f"Downloading {img_url} to {img_path}")
    response = requests.get(img_url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, "wb") as f:
            f.write(response.content)
    else:
        print(f"Error downloading {img_url}")


def download_images(url: str, size: int, step: int, offset: int) -> None:
    with ThreadPoolExecutor(max_workers=4) as executor:
        for i in range(-size + offset*step, 2 * size + 1 + offset*step, step):
            for j in range(-size + offset*step, 2 * size + 1 + offset*step, step):
                executor.submit(download_image, url, size, i, j, step)
        executor.shutdown(wait=True)


def image_count(size: int, step: int) -> int:
    return ((2 * size + size + 1) // step) ** 2


def print_small_files(folder_path: str) -> None:
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath) and os.path.getsize(filepath) < 150:
            print(filename, end="   ")


def delete_small_files(folder_path: str) -> None:
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath) and os.path.getsize(filepath) < 150:
            print(f"Deleting {filename}")
            os.remove(filepath)


if __name__ == "__main__":
    url = "http://play.warpedsmp.com:25572"

    size = 90
    step = 4
    offset = 12
    start_time = time.time()

    if "--help" in sys.argv:
        print("Usage: python dynmap_download.py [-d] [-c] [-s] [-f]")
        print("Options:")
        print("  -d: Delete existing images")
        print("  -c: Delete small files")
        print("  -s: Skip downloading images")
        print("  -f: Combine images")
        sys.exit()

    args = sys.argv[1:]
    if "-d" in args:    # Delete existing images
        files = glob.glob('output/*_*.jpg')
        for f in files:
            if os.path.isfile(f):
                os.remove(f)
        print("Deleted existing images.")

    if "-c" in args:    # Delete small files
        delete_small_files("output")

    if not "-s" in args:   # Skip downloading
        print(f"Downloading {image_count(size, step)} images.")
        download_images(url, size, step, offset)
        print("Done downloading images. Took %.2f seconds." %
              (time.time() - start_time))

    if "-f" in args:    # Combine images
        print("Combining images.")
        start_time = time.time()
        combine_images()
        print("Done combining images. Took %.2f seconds." %
              (time.time() - start_time))

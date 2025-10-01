# dynmap_download

Download tiles from a dynmap instance.

## Usage

- **Download images:**
  ```bash
  python dynmap_download.py <url> <radius>
  ```
- **Download and combine images:**
  ```bash
  python dynmap_download.py <url> <radius> -f
  ```
- **Only combine existing images:**
  ```bash
  python dynmap_download.py <url> <radius> -s -f
  ```
`<url>` is the URL of the dynmap instance and `<radius>` is the desired radius in blocks.
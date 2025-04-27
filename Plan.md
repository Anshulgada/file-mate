# Filemate: Command Structure and Feature Ideation (Revised)

This document outlines the planned command structure and features for the `filemate` CLI tool, organized primarily by file type or data category.

## Command Structure Tree

```
filemate
│
├── file // General file/directory operations
│   ├── rename .................. Rename files sequentially based on a pattern.
│   ├── change-ext ............ Change file extensions.
│   ├── organize .............. Organize files into subdirectories (by date, ext, etc.).
│   ├── duplicates ............ Find duplicate files by content hash.
│   ├── split ................. Split large files into smaller chunks.
│   ├── merge ................. Concatenate text-based files.
│   └── checksum .............. Calculate file checksums (MD5, SHA).
│
├── image // Image-specific processing and conversion
│   ├── convert ............... Convert single/batch images between formats (JPG, PNG, WEBP, etc.).
│   ├── resize ................ Resize image dimensions (pixels or scale).
│   ├── rotate ................ Rotate an image by specified degrees (90, 180, 270, custom).
│   ├── grayscale ............. Convert an image to grayscale.
│   ├── compress .............. Apply lossy/lossless compression (adjust quality).
│   ├── crop .................. Crop image to specified dimensions/coordinates.
│   ├── flip .................. Flip image horizontally or vertically.
│   ├── add-border ............ Add a solid color border around an image.
│   ├── add-text .............. Overlay text onto an image.
│   ├── make-transparent ...... Make a specific color transparent (simple cases).
│   ├── metadata-view ......... View image metadata (EXIF, etc.).
│   ├── metadata-remove ....... Remove image metadata.
│   ├── remove-bg ............. Remove image background [Advanced/API].
│   ├── upscale ............... Upscale image resolution [Advanced/ML Model].
│   └── (to-pdf/docx/etc. handled by `pdf convert from-image` / `doc convert from-image`)
│
├── pdf // PDF-specific processing and conversion
│   ├── convert ............... Convert PDF pages to images or extract text.
│   │   ├── to-images .......... Converts PDF pages into individual image files.
│   │   └── to-text ............ Extracts text content from PDF.
│   ├── create ................ Create PDFs from other file types.
│   │   ├── from-images ........ Creates a PDF from one or more image files.
│   │   └── from-text .......... Creates a basic PDF from a text file [Basic].
│   │   └── from-url ........... Creates a PDF from a web page URL [Complex].
│   │   └── (from-word/excel/etc. [Very Complex, likely requires external tools])
│   ├── manipulate ............ Modify existing PDFs.
│   │   ├── merge .............. Merge multiple PDF files into one.
│   │   ├── split .............. Split a PDF by page ranges, size, or bookmarks.
│   │   ├── compress ........... Reduce PDF file size.
│   │   ├── encrypt ............ Add password protection (owner/user).
│   │   ├── decrypt ............ Remove password protection (if password known).
│   │   ├── crop ............... Crop PDF page boundaries.
│   │   ├── rotate ............. Rotate PDF pages.
│   │   ├── add-watermark ...... Add text or image watermark to pages.
│   │   ├── add-pg-numbers .... Add page numbers to PDF pages.
│   │   ├── rearrange ......... Reorder pages within a PDF.
│   │   └── delete-pages ....... Remove specific pages from a PDF.
│   ├── extract ............... Extract content from PDFs.
│   │   ├── images ............ Extracts embedded images from a PDF.
│   │   └── text .............. (Same as `pdf convert to-text`, maybe alias or keep only one).
│   └── ocr ................... Apply OCR to make scanned PDFs searchable.
│
├── text // Operations on text-based structured data
│   ├── convert ............... Convert between text formats (CSV, JSON, XML, potentially Excel).
│   │   ├── csv-to-json ....... Converts CSV data to JSON format.
│   │   ├── json-to-csv ....... Converts JSON data (list of objects) to CSV.
│   │   ├── csv-to-xml ........ Converts CSV data to XML format.
│   │   ├── xml-to-csv ........ Converts XML data to CSV (structure assumptions needed).
│   │   ├── json-to-xml ....... Converts JSON data to XML.
│   │   ├── xml-to-json ....... Converts XML data to JSON.
│   │   └── (Excel conversions [More Complex])
│   ├── split ................. Split text/CSV files (by lines, size).
│   └── merge ................. Merge text/CSV files.
│
└── info <file_path> .......... Get detailed info about any file (Top Level).
```

---

## Detailed Command Group Descriptions

### 1. `file` Group

**Focus:** General operations on files and directories irrespective of content type.

*   **`file rename <folder> [OPTIONS]`**
    *   **Description:** Sequentially renames files using `{i}` pattern. Sorts alphanumerically first. Handles conflicts.
    *   **Key Options:** `--pattern`, `--ext` (filter source), `--start`, `--output-dir`, `--dry-run`.
    *   **Libraries:** `pathlib`, `os`.

*   **`file change-ext <folder> [OPTIONS]`**
    *   **Description:** Changes file extensions. Can filter by source extension(s).
    *   **Key Options:** `--to` (required, target ext), `--from` (source ext(s)), `--output-dir`, `--dry-run`.
    *   **Libraries:** `pathlib`, `os`, `shutil`.

*   **`file organize <folder> [OPTIONS]`**
    *   **Description:** Moves files from `<folder>` into subdirectories based on criteria.
    *   **Key Options:** `--by [date|extension|type]`, `--date-format [YYYY|YYYY-MM|YYYY-MM-DD]`, `--output-dir`, `--copy` (instead of move), `--dry-run`.
    *   **Libraries:** `pathlib`, `os`, `shutil`, `python-magic`.

*   **`file duplicates <folder> [OPTIONS]`**
    *   **Description:** Finds files with identical content within `<folder>` using hashing.
    *   **Key Options:** `--hash [md5|sha1|sha256]`, `--delete` (use with extreme caution), `--output-file` (report), `--min-size`.
    *   **Libraries:** `pathlib`, `os`, `hashlib`.

*   **`file split <input_file> [OPTIONS]`**
    *   **Description:** Splits a large file into smaller chunks.
    *   **Key Options:** `--by-size <size>` (e.g., 100M), `--by-lines <num_lines>`, `--output-dir`, `--prefix` (for chunk names).
    *   **Libraries:** `pathlib`, `os`.

*   **`file merge <input_files...> <output_file>`**
    *   **Description:** Concatenates multiple text-based files into a single output file. Accepts multiple input files.
    *   **Key Options:** *(Maybe `--separator`)*.
    *   **Libraries:** `pathlib`, `shutil`.

*   **`file checksum <file_path> [OPTIONS]`**
    *   **Description:** Computes and displays the checksum (hash) of a file.
    *   **Key Options:** `--hash [md5|sha1|sha256]` (default md5 or sha256).
    *   **Libraries:** `pathlib`, `hashlib`.

### 2. `image` Group

**Focus:** Processing and converting raster and vector image files.

*   **`image convert <input...> <output> [OPTIONS]`**
    *   **Description:** Converts image(s) between formats. Handles single file (`<input> <output>`) or batch (`<input_dir> <output_dir>`). Input can be multiple files for formats like GIF/multi-page TIFF.
    *   **Key Options:** `--format` (target, e.g., jpg, png, webp, gif, tiff, bmp, heic, avif), `--quality` (for lossy), `--input-dir`, `--output-dir`, `--recursive`.
    *   **Libraries:** `Pillow`, `pillow-heif`, `pillow-avif-plugin` (or external libs).

*   **`image resize <input> <output> [OPTIONS]`**
    *   **Description:** Resizes image dimensions. Maintains aspect ratio by default if only one dimension is given.
    *   **Key Options:** `--width <px>`, `--height <px>`, `--scale <factor>`, `--force` (ignore aspect ratio if W&H given).
    *   **Libraries:** `Pillow`.

*   **`image rotate <input> <output> --degrees <angle>`**
    *   **Description:** Rotates image.
    *   **Key Options:** `--degrees` (e.g., 90, 180, 270, or float), `--expand` (resize canvas to fit).
    *   **Libraries:** `Pillow`.

*   **`image grayscale <input> <output>`**
    *   **Description:** Converts image to grayscale.
    *   **Libraries:** `Pillow`.

*   **`image compress <input> <output> [OPTIONS]`**
    *   **Description:** Reduces image file size, adjusting quality or using optimization.
    *   **Key Options:** `--quality` (0-100 for lossy), `--optimize` (flag for lossless), `--format` (can convert too).
    *   **Libraries:** `Pillow`.

*   **`image crop <input> <output> [OPTIONS]`**
    *   **Description:** Crops image to a specified rectangle.
    *   **Key Options:** `--box <left,top,right,bottom>`, or `--coords <x,y,w,h>`.
    *   **Libraries:** `Pillow`.

*   **`image flip <input> <output> --direction [horizontal|vertical]`**
    *   **Description:** Flips image.
    *   **Libraries:** `Pillow`.

*   **`image add-border <input> <output> [OPTIONS]`**
    *   **Description:** Adds a solid border.
    *   **Key Options:** `--width <px>`, `--color <name_or_hex>`.
    *   **Libraries:** `Pillow`, `PIL.ImageOps.expand`.

*   **`image add-text <input> <output> --text <string> [OPTIONS]`**
    *   **Description:** Overlays text.
    *   **Key Options:** `--text`, `--position [top-left|center|...]`, `--font <path_or_name>`, `--size <pt>`, `--color`.
    *   **Libraries:** `Pillow`, `PIL.ImageDraw`, `PIL.ImageFont`.

*   **`image make-transparent <input> <output> --color <hex_or_rgb>`**
    *   **Description:** Makes pixels of a specific color transparent (best for simple images/palettes).
    *   **Libraries:** `Pillow`.

*   **`image metadata-view <input>`**
    *   **Description:** Displays EXIF and other metadata.
    *   **Libraries:** `Pillow`.

*   **`image metadata-remove <input> <output>`**
    *   **Description:** Creates a copy of the image with metadata stripped.
    *   **Libraries:** `Pillow`.

*   **`image remove-bg <input> <output>`** [Advanced/API]
    *   **Description:** Attempts to remove the image background.
    *   **Libraries:** Requires specialized ML libraries (`rembg`) or external APIs.

*   **`image upscale <input> <output> [OPTIONS]`** [Advanced/ML Model]
    *   **Description:** Increases image resolution using AI models.
    *   **Key Options:** `--scale <factor>`.
    *   **Libraries:** Requires specialized ML libraries (`realesrgan-ncnn-py` etc.)

### 3. `pdf` Group

**Focus:** Creating, manipulating, converting, and extracting data from PDF documents.

*   **`pdf convert to-images <input_pdf> <output_dir> [OPTIONS]`**
    *   **Description:** Converts each PDF page to an image file.
    *   **Key Options:** `--format` (png, jpg, etc.), `--prefix` (output name), `--dpi`.
    *   **Libraries:** `pypdf` (read), `Pillow` (save), potentially `PyMuPDF` or `poppler` bindings for rendering.

*   **`pdf convert to-text <input_pdf> [output_file]`**
    *   **Description:** Extracts text content. Output to file or stdout.
    *   **Key Options:** `--pages <range>`, `--layout` (try to preserve layout).
    *   **Libraries:** `pypdf`, potentially `PyMuPDF` or `pdfplumber` for better results.

*   **`pdf create from-images <input_images...> <output_pdf>`**
    *   **Description:** Creates a single PDF from one or more images.
    *   **Libraries:** `Pillow` (read images), `reportlab` / `fpdf2` (write PDF).

*   **`pdf create from-text <input_txt> <output_pdf> [OPTIONS]`** [Basic]
    *   **Description:** Creates a simple, text-flow PDF from a text file.
    *   **Key Options:** `--font`, `--size`.
    *   **Libraries:** `reportlab` / `fpdf2`.

*   **`pdf create from-url <url> <output_pdf>`** [Complex]
    *   **Description:** Renders a web page to PDF.
    *   **Libraries:** Requires browser automation (`playwright`, `selenium`) or specialized HTML-to-PDF libraries (`weasyprint`, `xhtml2pdf`).

*   **`pdf manipulate merge <input_pdfs...> <output_pdf>`**
    *   **Description:** Merges multiple PDFs sequentially.
    *   **Libraries:** `pypdf`.

*   **`pdf manipulate split <input_pdf> [OPTIONS]`**
    *   **Description:** Splits PDF into multiple files.
    *   **Key Options:** `--by-pages <ranges>` (e.g., 1-3,5,7-), `--by-size <MB>`, `--output-dir`, `--prefix`.
    *   **Libraries:** `pypdf`.

*   **`pdf manipulate compress <input_pdf> <output_pdf> [OPTIONS]`**
    *   **Description:** Reduces file size (often by optimizing images/fonts).
    *   **Key Options:** `--level [low|medium|high]`.
    *   **Libraries:** `pypdf` (basic options), potentially external tools like `ghostscript` for better results.

*   **`pdf manipulate encrypt <input_pdf> <output_pdf> [OPTIONS]`**
    *   **Description:** Adds password protection.
    *   **Key Options:** `--user-pw <pw>`, `--owner-pw <pw>`, `--allow [print|copy|...]`.
    *   **Libraries:** `pypdf`.

*   **`pdf manipulate decrypt <input_pdf> <output_pdf> --password <pw>`**
    *   **Description:** Removes password if known.
    *   **Libraries:** `pypdf`.

*   **`pdf manipulate crop <input_pdf> <output_pdf> [OPTIONS]`**
    *   **Description:** Crops page boundaries (modifies CropBox/MediaBox).
    *   **Key Options:** `--box <left,bottom,right,top>` (points), `--pages <range>`.
    *   **Libraries:** `pypdf`.

*   **`pdf manipulate rotate <input_pdf> <output_pdf> [OPTIONS]`**
    *   **Description:** Rotates specified pages.
    *   **Key Options:** `--degrees <90|180|270>`, `--pages <range>`.
    *   **Libraries:** `pypdf`.

*   **`pdf manipulate add-watermark <input_pdf> <output_pdf> [OPTIONS]`**
    *   **Description:** Adds a text or image watermark.
    *   **Key Options:** `--text <string>`, `--image <path>`, `--opacity`, `--pages`, `--position`.
    *   **Libraries:** `pypdf`, `reportlab` (for creating watermark PDF).

*   **`pdf manipulate add-pg-numbers <input_pdf> <output_pdf> [OPTIONS]`**
    *   **Description:** Adds page numbers.
    *   **Key Options:** `--position`, `--start-page`, `--format`, `--font-size`.
    *   **Libraries:** `pypdf`, `reportlab`.

*   **`pdf manipulate rearrange <input_pdf> <output_pdf> --order <page_spec>`**
    *   **Description:** Reorders pages based on specification (e.g., '1,5,3-4,2').
    *   **Libraries:** `pypdf`.

*   **`pdf manipulate delete-pages <input_pdf> <output_pdf> --pages <range>`**
    *   **Description:** Removes specified pages.
    *   **Libraries:** `pypdf`.

*   **`pdf extract images <input_pdf> <output_dir>`**
    *   **Description:** Extracts embedded images.
    *   **Libraries:** `pypdf` or `PyMuPDF`.

*   **`pdf extract text <input_pdf> [output_file]`**
    *   **Description:** (Same as `pdf convert to-text`). Extracts text.
    *   **Libraries:** `pypdf`, `PyMuPDF`, `pdfplumber`.

*   **`pdf ocr <input_pdf> <output_pdf> [OPTIONS]`**
    *   **Description:** Adds a text layer to scanned PDFs using OCR.
    *   **Key Options:** `--language`, `--force-ocr`.
    *   **Libraries:** Wrapper around `ocrmypdf` CLI tool (requires `ocrmypdf` and its dependencies like Tesseract to be installed separately).

### 4. `text` Group

**Focus:** Operations on structured text data formats.

*   **`text convert <input> <output> --from-format <fmt> --to-format <fmt>`**
    *   **Description:** Converts between CSV, JSON (list of objects), XML (simple structures). Maybe basic Excel.
    *   **Key Options:** Specific format options (e.g., `--csv-delimiter`, `--json-indent`, `--xml-root-tag`).
    *   **Libraries:** `csv`, `json`, `xml.etree.ElementTree`, potentially `pandas`, `openpyxl`.

*   **`text split <input> [OPTIONS]`**
    *   **Description:** Splits text/CSV files.
    *   **Key Options:** `--by-lines <num>`, `--by-size <bytes>`, `--output-dir`, `--prefix`, `--keep-header` (for CSV).
    *   **Libraries:** `pathlib`, `os`, `csv`.

*   **`text merge <inputs...> <output>`**
    *   **Description:** Merges text/CSV files.
    *   **Key Options:** `--skip-headers` (for CSV).
    *   **Libraries:** `pathlib`, `shutil`, `csv`.

### 5. Top-Level Commands

*   **`info <file_path>`**
    *   **Description:** Auto-detects file type and displays relevant information (size, type, image dimensions, PDF pages, etc.). Acts as a dispatcher to type-specific info logic.
    *   **Libraries:** `python-magic`, `Pillow`, `pypdf`, `os`, `pathlib`.

---

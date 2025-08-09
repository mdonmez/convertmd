# convertmd

A web application for converting documents to Markdown format. Convert PDF, Word, PowerPoint, and Excel files to clean Markdown with ease.

[Try it now](https://dub.sh/convertmd)

## Features

- **Multiple Format Support**: Convert PDF, DOCX, DOC, PPTX, PPT, XLSX, and XLS files
- **Single & Batch Processing**: Convert individual files or multiple files at once with multithreading
- **Real-time Preview**: View converted Markdown before downloading
- **ZIP Archive Export**: Batch conversions are packaged as ZIP files

## Quick Start

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mdonmez/convertmd
   cd convertmd
   ```

2. **Install dependencies using uv**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run streamlit run main.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501` to use the application.

## Usage

### Single File Conversion

1. Upload a single document using the file uploader
2. Wait for the conversion to complete
3. Preview the Markdown content (optional)
4. Download the converted `.md` file

### Batch Conversion

1. Upload multiple documents at once
2. Monitor the progress bar as files are processed in parallel
3. Review any conversion errors if they occur
4. Download the ZIP archive containing all converted Markdown files

### Supported File Types

`.pdf`, `.docx`, `.doc`, `.pptx`, `.ppt`, `.xlsx`, `.xls`

## Architecture

The application is built with:

- **[Streamlit](https://streamlit.io/)**: Web interface framework
- **[MarkItDown](https://github.com/microsoft/markitdown)**: Document conversion engine
- **ThreadPoolExecutor**: Parallel processing for batch conversions
- **In-memory ZIP creation**: Efficient batch file packaging

## Troubleshooting

### Common Issues

1. **Conversion Fails**: Ensure the uploaded file is not corrupted and is in a supported format
2. **Performance Issues**: Large files or many simultaneous conversions may take time
3. **Memory Usage**: Very large files might consume significant memory during processing

### Error Messages

- **"No content extracted"**: The file may be empty, corrupted, or in an unsupported format

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

# License

This project is licensed under the MIT License. Look [LICENSE](LICENSE) for more information.

## Acknowledgments

- [MarkItDown](https://github.com/microsoft/markitdown) for the powerful document conversion engine
- [Streamlit](https://streamlit.io/) for the excellent web framework
- [uv](https://docs.astral.sh/uv/) for fast Python package management

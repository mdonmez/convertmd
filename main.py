import streamlit as st
import tempfile
import os
import zipfile
import io
from markitdown import MarkItDown
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configure page
st.set_page_config(page_title="convertmd", page_icon="📄", layout="centered")

# Minimal CSS
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


def convert_document(uploaded_file):
    """Quick document conversion"""
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=f"_{uploaded_file.name}"
    ) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        md_converter = MarkItDown()
        result = md_converter.convert(tmp_file_path)
        os.unlink(tmp_file_path)

        if result and result.text_content:
            return result.text_content, None
        else:
            return None, "No content extracted"
    except Exception as e:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        return None, str(e)


def convert_batch(uploaded_files):
    """Convert multiple files in parallel and return as zip"""
    converted_files = []
    errors = []

    progress_bar = st.progress(0)
    status_text = st.empty()
    completed_count = 0
    total_files = len(uploaded_files)

    # Thread-safe counter for progress updates
    progress_lock = threading.Lock()

    def update_progress(filename):
        nonlocal completed_count
        with progress_lock:
            completed_count += 1
            status_text.text(f"Completed {completed_count}/{total_files} files...")
            progress_bar.progress(completed_count / total_files)

    def convert_single_file(file):
        """Convert a single file and return result"""
        try:
            content, error = convert_document(file)
            update_progress(file.name)

            if content:
                filename = f"{Path(file.name).stem}.md"
                return (filename, content, None)
            else:
                return (None, None, f"{file.name}: {error}")
        except Exception as e:
            update_progress(file.name)
            return (None, None, f"{file.name}: {str(e)}")

    # Use ThreadPoolExecutor with max 5 workers
    with ThreadPoolExecutor(max_workers=min(5, total_files)) as executor:
        # Submit all conversion tasks
        future_to_file = {
            executor.submit(convert_single_file, file): file for file in uploaded_files
        }

        # Process completed futures
        for future in as_completed(future_to_file):
            filename, content, error = future.result()
            if content:
                converted_files.append((filename, content))
            else:
                errors.append(error)

    progress_bar.empty()
    status_text.empty()

    if converted_files:
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in converted_files:
                zip_file.writestr(filename, content)

        zip_buffer.seek(0)
        return zip_buffer.getvalue(), errors
    else:
        return None, errors


def main():
    # Initialize session state
    if "converted_files_data" not in st.session_state:
        st.session_state.converted_files_data = {}  # Dict: filename -> content
    if "conversion_errors" not in st.session_state:
        st.session_state.conversion_errors = {}  # Dict: filename -> error
    if "last_files" not in st.session_state:
        st.session_state.last_files = []
    if "clear_files" not in st.session_state:
        st.session_state.clear_files = False

    # Header
    st.markdown("# convertmd")
    st.markdown("*Easily convert any document to Markdown*")

    # Single file uploader that accepts multiple files
    uploaded_files = st.file_uploader(
        "Upload Document(s)",
        type=["pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "epub"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Drag and drop file(s) here, or click to browse",
        key="file_uploader"
        if not st.session_state.clear_files
        else "file_uploader_cleared",
    )

    # Clear all button (only show when files are uploaded)
    if uploaded_files:
        if st.button("Clear All", type="secondary", use_container_width=False):
            # Set flag to clear files and reset session state
            st.session_state.clear_files = not st.session_state.clear_files
            st.session_state.converted_files_data = {}
            st.session_state.conversion_errors = {}
            st.session_state.last_files = []
            st.rerun()

    if uploaded_files:
        # Check which files have been removed and which are new
        current_file_names = [f.name for f in uploaded_files]
        previous_file_names = set(st.session_state.last_files)
        current_file_names_set = set(current_file_names)

        # Remove data for files that are no longer uploaded
        removed_files = previous_file_names - current_file_names_set
        for removed_file in removed_files:
            st.session_state.converted_files_data.pop(removed_file, None)
            st.session_state.conversion_errors.pop(removed_file, None)

        # Find new files that need conversion
        new_files = [
            f
            for f in uploaded_files
            if f.name not in st.session_state.converted_files_data
        ]

        # Convert new files
        if new_files:
            if len(new_files) == 1:
                # Single file - convert directly
                file = new_files[0]
                with st.spinner(f"Converting {file.name}..."):
                    content, error = convert_document(file)
                if content:
                    st.session_state.converted_files_data[file.name] = content
                    st.session_state.conversion_errors.pop(
                        file.name, None
                    )  # Remove any previous error
                else:
                    st.session_state.conversion_errors[file.name] = error
                    st.session_state.converted_files_data.pop(
                        file.name, None
                    )  # Remove any previous content
            else:
                # Multiple files - use parallel processing
                with st.spinner(f"Converting {len(new_files)} files..."):

                    def convert_and_store(file):
                        content, error = convert_document(file)
                        return file.name, content, error

                    # Use ThreadPoolExecutor for parallel conversion
                    with ThreadPoolExecutor(
                        max_workers=min(5, len(new_files))
                    ) as executor:
                        # Submit all conversion tasks
                        future_to_filename = {
                            executor.submit(convert_and_store, file): file.name
                            for file in new_files
                        }

                        # Process completed futures
                        for future in as_completed(future_to_filename):
                            filename, content, error = future.result()
                            if content:
                                st.session_state.converted_files_data[filename] = (
                                    content
                                )
                                st.session_state.conversion_errors.pop(
                                    filename, None
                                )  # Remove any previous error
                            else:
                                st.session_state.conversion_errors[filename] = error
                                st.session_state.converted_files_data.pop(
                                    filename, None
                                )  # Remove any previous content

        # Update last files list
        st.session_state.last_files = current_file_names

        # Handle single file
        if len(uploaded_files) == 1:
            uploaded_file = uploaded_files[0]
            content = st.session_state.converted_files_data.get(uploaded_file.name)
            error = st.session_state.conversion_errors.get(uploaded_file.name)

            if content:
                st.success("Converted!")

                # Quick stats
                words = len(content.split())
                st.caption(f"{words:,} words • {len(content.splitlines())} lines")

                # Download
                filename = f"{Path(uploaded_file.name).stem}.md"
                st.download_button(
                    "Download Markdown",
                    data=content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )

                # Preview
                with st.expander("Preview", expanded=False):
                    st.code(content, language="markdown")
            else:
                st.error(f"Error: {error}")

        # Handle multiple files
        else:
            # Get converted files and errors for current uploads
            converted_files = []
            errors = []

            for file in uploaded_files:
                if file.name in st.session_state.converted_files_data:
                    filename = f"{Path(file.name).stem}.md"
                    content = st.session_state.converted_files_data[file.name]
                    converted_files.append((filename, content))
                elif file.name in st.session_state.conversion_errors:
                    errors.append(
                        f"{file.name}: {st.session_state.conversion_errors[file.name]}"
                    )

            # Create zip if we have converted files
            zip_data = None
            if converted_files:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for filename, content in converted_files:
                        zip_file.writestr(filename, content)
                zip_buffer.seek(0)
                zip_data = zip_buffer.getvalue()

            if zip_data:
                st.success(
                    f"Batch conversion complete! {len(uploaded_files) - len(errors)} files converted."
                )

                if errors:
                    with st.expander("Conversion Errors", expanded=False):
                        for error in errors:
                            st.error(error)

                # Download zip
                st.download_button(
                    "Download ZIP Archive",
                    data=zip_data,
                    file_name="converted_markdown_files.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
            else:
                st.error("No files could be converted. Check the error details above.")

    else:
        # Clear session state when no files are uploaded
        st.session_state.converted_files_data = {}
        st.session_state.conversion_errors = {}
        st.session_state.last_files = []
        # Show supported formats info only if no file is uploaded
        st.info("**Supported formats:** PDF, Word, PowerPoint, Excel")
        st.caption("Single file -> Direct download | Multiple files -> ZIP archive")


if __name__ == "__main__":
    main()

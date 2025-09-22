# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based syllabus converter application that extracts syllabus URLs from HTML files and converts them to PDF format. The application consists of three main modules:

1. **syllabus_converter.py** - Main application that searches for HTML files containing syllabus URLs and batch converts them to PDFs
2. **print_pdf.py** - Simple URL-to-PDF converter that processes a list of URLs from a text file
3. **debug_html.py** - Debugging utility to inspect HTML files and identify syllabus URL patterns

## Core Architecture

### URL Pattern Matching
The application specifically targets syllabus URLs with the pattern:
- `https://[domain]/path/SyllabusHtml.2025.[CourseID].html`
- Course IDs are alphanumeric (A-Za-z0-9)
- Uses BeautifulSoup for HTML parsing and regex for URL extraction

### File Processing Flow
1. **HTML Discovery**: Recursively searches directories for .html files
2. **URL Extraction**: Parses HTML content to find matching syllabus URLs
3. **PDF Conversion**: Uses pdfkit to convert URLs to PDF files
4. **Output Organization**: Creates subdirectories based on source HTML directory structure

### Dependencies
- `pdfkit` - PDF generation from URLs
- `BeautifulSoup4` - HTML parsing
- `os`, `re`, `glob` - File operations and pattern matching
- `urllib.parse` - URL parsing

## Development Commands

Since this is a standalone Python application without a package manager setup, run scripts directly:

```bash
# Main syllabus converter
python syllabus_converter.py

# Simple URL-to-PDF converter
python print_pdf.py

# Debug HTML content
python debug_html.py
```

## Key Functions

- `extract_syllabus_urls()` - Core URL extraction logic in syllabus_converter.py:12
- `convert_url_to_pdf()` - PDF conversion wrapper in syllabus_converter.py:43
- `sanitize_filename()` - File name cleaning utility used across modules
- `extract_course_id()` - Extracts course ID from syllabus URLs in syllabus_converter.py:38

## File Naming Convention

PDFs are saved using the extracted course ID as the filename (e.g., `ABC123.pdf`). The application handles duplicate prevention by checking for existing files before conversion.
# Pricebook Data Extraction AI

This Streamlit application allows users to extract series, options, and pricing information from visual Pricebooks (PDFs) using AI. It supports both **Weaviate** and **Google Gemini** as backend models.

## Features

-   **Multi-Model Support**: Toggle between Weaviate (RAG) and Gemini (Direct Context).
-   **PDF Upload**: Upload Pricebook PDFs directly when using Gemini.
-   **Dynamic Prompts**: Edit and save prompts directly within the application using the side-by-side Editor. Externalized to `prompts.json`.
-   **Interactive UI**: Step-by-step selection flow (Series -> Options -> Price).

## Prerequisites

-   Python 3.8+
-   API Keys:
    -   Running local or cloud Weaviate instance (configured in `agent.py`).
    -   Google Gemini API Key (configured in `gemini.py` or `agent.py`).

## Installation

1.  Clone existing repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the Streamlit app:
    ```bash
    streamlit run streamlit_app.py
    ```
2.  **Configuration (Sidebar)**:
    -   Select **Weaviate** or **Gemini**.
    -   If **Gemini** is selected, upload your Pricebook PDF.
3.  **Extraction Flow**:
    -   **Prompt Editor (Right Panel)**: Verify or edit the prompts used for extraction. Click "Save Prompts" if you make changes.
    -   **Main App (Left Panel)**:
        -   Click **GET SERIES NAMES** to extract the list of series from the pricebook.
        -   Select a Series and click **Submit**.
        -   Select the product options (Model, Finish, Size, etc.) populated dynamically.
        -   Click **Submit Product Selection** to get the final price.

## Configuration Files

-   `prompts.json`: Stores the prompts for Indexing, Option Extraction, and Price Extraction.
-   `agent.py`: Weaviate connection and query logic.
-   `gemini.py`: Gemini API connection and file upload logic.
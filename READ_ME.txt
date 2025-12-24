Pricebook Data Extraction App
=============================

HOW TO RUN:
1. Install requirements: pip install -r requirements.txt
2. Run App: streamlit run streamlit_app.py

FEATURES:
- Choose between Weaviate and Gemini AI from the sidebar.
- Upload PDF directly for Gemini.
- Edit Prompts on the right-side panel. Prompts are saved to prompts.json.

USAGE:
1. Select AI Model.
2. Upload PDF (if Gemini).
3. Click "GET SERIES NAMES".
4. Select Series -> Submit.
5. Select Options -> Submit.
6. View Price.

FILES:
- streamlit_app.py: Main application.
- prompts.json: Editable prompts.
- agent.py: Weaviate logic.
- gemini.py: Gemini logic.
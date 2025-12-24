import streamlit as st
import time
import tempfile
import os
import json

from agent import get_final_data as get_weaviate_data
from gemini import upload_pdf, get_gemini_response

# ------------------------
# Configuration & Setup
# ------------------------
st.set_page_config(layout="wide") # Use wide mode for better column layout

PROMPTS_FILE = "prompts.json"

def load_prompts():
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prompts(prompts):
    with open(PROMPTS_FILE, "w") as f:
        json.dump(prompts, f, indent=4)


# Load prompts into session state if not present
if "prompts" not in st.session_state:
    st.session_state.prompts = load_prompts()

# ------------------------
# Streamlit UI Layout
# ------------------------

# Main Layout: Left (App) and Right (Prompt Editor)
col1, col2 = st.columns([0.7, 0.3])

# --- RIGHT COLUMN: Prompt Editor ---
with col2:
    st.header("📝 Prompt Editor")
    with st.expander("Edit Prompts", expanded=True):
        
        # Series Index Prompt
        new_index_prompt = st.text_area("Index Prompt", value=st.session_state.prompts.get("prompt_index", ""), height=150)
        
        # Options Identification Prompt
        st.info("Variables: `{series_name}`")
        new_test_prompt = st.text_area("Options Prompt", value=st.session_state.prompts.get("prompt_test", ""), height=150)
        
        # Price Extraction Prompt
        st.info("Variables: `{series}`, `{selection}`")
        new_price_prompt = st.text_area("Price Prompt", value=st.session_state.prompts.get("price_prompt", ""), height=150)
        
        if st.button("💾 Save Prompts"):
            st.session_state.prompts["prompt_index"] = new_index_prompt
            st.session_state.prompts["prompt_test"] = new_test_prompt
            st.session_state.prompts["price_prompt"] = new_price_prompt
            save_prompts(st.session_state.prompts)
            st.success("Prompts Saved!")
            time.sleep(1)
            st.rerun()


# --- LEFT COLUMN: Main App ---
with col1:
    st.title("Pricebook Data Extraction Using AI")

    # Sidebar for Model Selection (Global)
    st.sidebar.header("Configuration")
    model_choice = st.sidebar.radio("Select AI Model", ("Weaviate", "Gemini"))

    pdf_file_obj = None

    if model_choice == "Gemini":
        uploaded_file = st.sidebar.file_uploader("Upload Pricebook PDF", type=["pdf"])
        
        if uploaded_file is not None:
            # Check if we already processed this file
            if "last_uploaded_filename" not in st.session_state or st.session_state.last_uploaded_filename != uploaded_file.name:
                # New file uploaded or first time upload
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                with st.spinner("Uploading PDF to Gemini..."):
                    pdf_file_obj = upload_pdf(tmp_path)
                    st.session_state.gemini_file_obj = pdf_file_obj
                    st.session_state.gemini_file_path = tmp_path
                    st.session_state.last_uploaded_filename = uploaded_file.name
                    st.success("PDF Uploaded to Gemini!")
            else:
                # File already processed, use cached object
                pdf_file_obj = st.session_state.gemini_file_obj
                # Optionally show a small message or just nothing to indicate readiness
                st.sidebar.info(f"Using uploaded file: {uploaded_file.name}")
        else:
            st.warning("Please upload a PDF to use Gemini.")


    # Helper function to get data based on selection
    def get_data(prompt_text):
        if model_choice == "Weaviate":
            return get_weaviate_data(prompt_text)
        elif model_choice == "Gemini":
            if "gemini_file_obj" in st.session_state:
                 return get_gemini_response(st.session_state.gemini_file_obj, prompt_text)
            else:
                st.error("No PDF uploaded for Gemini.")
                return []
        return []

    # Step 1 — load series
    if st.button("GET SERIES NAMES"):
        # Use dynamic prompt
        index_prompt = st.session_state.prompts.get("prompt_index", "")
        data = get_data(index_prompt)
        if data:
            st.session_state.series_list = [d["SERIES"] for d in data]
            st.success("Series Loaded Successfully!")

    # Step 2 & 3 — series selection
    if "series_list" in st.session_state:
        selected_series = st.selectbox("Select a Series", st.session_state.series_list)

        if st.button("Submit Series Selection"):
            st.session_state.step3_done = True
            st.session_state.selected_series_name = selected_series # Store to use later
            st.toast("Thank you! Series selected 🎉")


    # Step 4 — Dynamic Product Options
    if st.session_state.get("step3_done", False):

        st.subheader("Select Product Details")
        
        # Use stored series name
        current_series = st.session_state.get("selected_series_name", "")

        # Clean up previous session state if series changed (optional logic, kept simple for now)
        # Use dynamic prompt with formatting
        raw_options_prompt = st.session_state.prompts.get("prompt_test", "")
        try:
             options_prompt = raw_options_prompt.format(series_name=current_series)
        except Exception as e:
             st.error(f"Error formatting prompt: {e}")
             options_prompt = raw_options_prompt # Fallback

        
        # Only fetch options if not already in session state OR if we want to refresh relative to the series
        if "dynamic_options" not in st.session_state:
             st.session_state.dynamic_options = get_data(options_prompt)
        
        # Store user selections here
        if "product_selections" not in st.session_state:
            st.session_state.product_selections = {}

        # Generate UI dynamically
        if st.session_state.dynamic_options:
            for key, values in st.session_state.dynamic_options.items():
                user_choice = st.selectbox(f"Select {key}", values, key=f"dyn_{key}")
                st.session_state.product_selections[key] = user_choice

            # Submit
            if st.button("Submit Product Selection"):
                with st.spinner("Processing your selection... ⏳ Please wait..."):
                    time.sleep(2) # Fake processing delay from original code

                st.session_state.product_done = True
                st.success("🎉 Product details submitted successfully!")
        else:
            st.warning("Could not load options. Please try again.")


    # Step 5 — Price display
    if st.session_state.get("product_done", False):

        st.subheader("Price Details")
        current_series = st.session_state.get("selected_series_name", "")
        
        # user selections string representation
        selection_str = str(st.session_state.product_selections)
        
        raw_price_prompt = st.session_state.prompts.get("price_prompt", "")
        try:
            pricePrompt = raw_price_prompt.format(series=current_series, selection=selection_str)
        except Exception as e:
             st.error(f"Error formatting price prompt: {e}")
             pricePrompt = raw_price_prompt

        price_list = get_data(pricePrompt)
        
        if price_list:
            try:
                # Handle potential variation in response structure between Weaviate/Gemini if any
                price = price_list[0]["price"]
                st.info(f"💰 Final Price Based on Your Selection: **{price}**")
            except (IndexError, KeyError, TypeError):
                 st.error(f"Could not extract price from response: {price_list}")
        else:
            st.error("No price data returned.")

        # Also show user’s choices (optional)
        st.write("Your Selections:", st.session_state.product_selections)

    

import streamlit as st
import json
import os
import tempfile
from gemini import upload_pdf, get_gemini_response

# Page configuration
st.set_page_config(page_title="Pricebook AI", page_icon="📖", layout="wide")

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #262730;
        color: white;
        border: 1px solid #4b4b4b;
    }
    .stButton>button:hover {
        background-color: #3d3f4b;
        border-color: #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'upload_completed' not in st.session_state:
    st.session_state.upload_completed = False
if 'sample_file' not in st.session_state:
    st.session_state.sample_file = None
if 'series_data' not in st.session_state:
    st.session_state.series_data = None
if 'current_prompts' not in st.session_state:
    if os.path.exists('prompt.json'):
        with open('prompt.json', 'r') as f:
            st.session_state.current_prompts = json.load(f)

st.title("📖 Pricebook AI")
st.subheader("Dynamic Series Extractor")

# Sidebar: Prompt Configuration
with st.sidebar:
    st.header("⚙️ Prompt Configuration")
    with st.expander("Edit Prompts", expanded=False):
        temp_prompts = {}
        for key, value in st.session_state.current_prompts.items():
            st.markdown(f"**{key.replace('_', ' ').title()}**")
            p_text = st.text_area(f"Prompt", value=value['prompt'], key=f"edit_p_{key}", height=150)
            e_json = st.text_area(f"Example (JSON)", value=json.dumps(value['example'], indent=2), key=f"edit_e_{key}", height=150)
            
            try:
                temp_prompts[key] = {
                    "prompt": p_text,
                    "example": json.loads(e_json)
                }
            except json.JSONDecodeError:
                st.error(f"Invalid JSON in {key} example")
                temp_prompts[key] = value # Revert to current if invalid

        if st.button("Save & Update Prompts"):
            st.session_state.current_prompts = temp_prompts
            # Persist to file
            with open('prompt.json', 'w') as f:
                json.dump(temp_prompts, f, indent=4)
            st.success("Prompts updated and saved!")
            st.rerun()

    if st.button("Start Over"):
        st.session_state.upload_completed = False
        st.session_state.sample_file = None
        st.session_state.series_data = None
        st.session_state.base_parameters = None
        st.session_state.additional_parameters = None
        st.rerun()

# Step 1: Upload PDF
if not st.session_state.upload_completed:
    uploaded_file = st.file_uploader("Upload Pricebook PDF", type=['pdf'], key="uploader")
    
    if uploaded_file is not None:
        with st.spinner("Uploading and processing PDF..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                st.session_state.sample_file = upload_pdf(tmp_path)
                st.session_state.upload_completed = True
                st.success("PDF Uploaded Successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error during upload: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

# Step 2: Get Series
if st.session_state.upload_completed and st.session_state.series_data is None:
    st.info("Upload complete. Ready to extract series names.")
    if st.button("Get Series"):
        with st.spinner("Extracting series details..."):
            try:
                p_config = st.session_state.current_prompts['toc_prompt']
                toc_prompt = p_config['prompt'] + "\nExample: " + json.dumps(p_config['example'])
                st.session_state.series_data = get_gemini_response(st.session_state.sample_file, toc_prompt)
                st.rerun()
            except Exception as e:
                st.error(f"Error getting series: {e}")

# Step 3: Select Series and Get Parameters
if st.session_state.series_data:
    st.success("Series names extracted!")
    
    series_list = [item['SERIES'] for item in st.session_state.series_data if 'SERIES' in item]
    selected_series = st.selectbox("Select a Series", options=series_list, key="series_selector")
    
    if 'base_parameters' not in st.session_state:
        st.session_state.base_parameters = None
    if 'additional_parameters' not in st.session_state:
        st.session_state.additional_parameters = None

    if st.button("Get Parameters"):
        with st.spinner(f"Extracting parameters for {selected_series}..."):
            try:
                # Get Base Parameters
                base_config = st.session_state.current_prompts['base_parameter_prompt']
                base_prompt = base_config['prompt'].format(series_name=selected_series)
                base_prompt += "\nExample: " + json.dumps(base_config['example'])
                st.session_state.base_parameters = get_gemini_response(st.session_state.sample_file, base_prompt)
                
                # Get Additional Parameters
                add_config = st.session_state.current_prompts['additional_parameter_prompt']
                additional_prompt = add_config['prompt'].format(series_name=selected_series)
                additional_prompt += "\nExample: " + json.dumps(add_config['example'])
                st.session_state.additional_parameters = get_gemini_response(st.session_state.sample_file, additional_prompt)
                
                st.success(f"Parameters extracted for {selected_series}!")
            except Exception as e:
                st.error(f"Error getting parameters: {e}")

# Step 4: Display Parameter Options
if st.session_state.get('base_parameters') or st.session_state.get('additional_parameters'):
    st.write("---")
    st.write(f"### Configuration for {st.session_state.get('series_selector')}")
    
    col1, col2 = st.columns(2)
    selections = {}
    
    with col1:
        if st.session_state.base_parameters:
            st.write("#### Base Parameters")
            for param, options in st.session_state.base_parameters.items():
                val = st.selectbox(f"Select {param}", options=options, key=f"base_{param}")
                selections[param] = val
                
    with col2:
        if st.session_state.additional_parameters:
            st.write("#### Additional Parameters")
            for param, options in st.session_state.additional_parameters.items():
                val = st.selectbox(f"Select {param}", options=options, key=f"add_{param}")
                selections[param] = val

    if st.button("Get Price"):
        with st.spinner("Calculating price and validating configuration..."):
            try:
                selection_text = json.dumps(selections, indent=2)
                
                price_config = st.session_state.current_prompts['price_prompt']
                price_prompt = price_config['prompt'].format(
                    series=st.session_state.get('series_selector'),
                    selection=selection_text
                )
                price_prompt += "\nExample: " + json.dumps(price_config['example'])
                
                price_response = get_gemini_response(st.session_state.sample_file, price_prompt)
                
                if isinstance(price_response, list) and len(price_response) > 0:
                    result = price_response[0]
                else:
                    result = price_response

                if result.get('is_valid'):
                    st.balloons()
                    st.metric("Final Price", f"${result.get('price')}")
                    st.success("Configuration is valid!")
                else:
                    st.error(f"Configuration Invalid: {result.get('reason')}")
                    st.warning("Please adjust your selections.")
                    
            except Exception as e:
                st.error(f"Error calculating price: {e}")

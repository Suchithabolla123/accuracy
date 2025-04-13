import streamlit as st
import pandas as pd
import json
import os
import tempfile

st.title("📊 Notebook Executor for Model Predictions")

# Upload components
uploaded_notebook = st.file_uploader("Upload a Colab Notebook (.ipynb)", type=["ipynb"])
train_file = st.file_uploader("Upload train.csv", type=["csv"])
test_file = st.file_uploader("Upload test.csv", type=["csv"])

# Proceed if all files are uploaded
if uploaded_notebook and train_file and test_file:
    st.success("✅ Files uploaded successfully!")

    # Step 1: Create temporary directory for the files
    temp_dir = tempfile.mkdtemp()

    # Step 2: Save uploaded CSVs temporarily to disk
    try:
        train_path = os.path.join(temp_dir, 'train.csv')
        test_path = os.path.join(temp_dir, 'test.csv')
        
        # Save uploaded CSV files to the temporary directory
        with open(train_path, 'wb') as f:
            f.write(train_file.getvalue())
        
        with open(test_path, 'wb') as f:
            f.write(test_file.getvalue())

        # Load the CSV files using pandas
        train = pd.read_csv(train_path)
        test = pd.read_csv(test_path)
        
        st.write("🟢 Train data preview:")
        st.dataframe(train.head())
        st.write("🟢 Test data preview:")
        st.dataframe(test.head())
        
    except Exception as e:
        st.error(f"Error saving/loading CSV files: {e}")

    # Step 3: Load and parse the notebook
    try:
        notebook = json.load(uploaded_notebook)
    except Exception as e:
        st.error(f"❌ Failed to read notebook: {e}")
        st.stop()

    st.info("📘 Executing code cells from the uploaded notebook...")

    # Step 4: Execute code cells
    for i, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") == "code":
            code = "".join(cell.get("source", []))
            st.subheader(f"Code Cell {i+1}")
            st.code(code, language="python")
            try:
                # Pass the file paths to the notebook code (this will make it work with the 'train.csv' and 'test.csv')
                globals()['train'] = train
                globals()['test'] = test
                globals()['train_path'] = train_path
                globals()['test_path'] = test_path
                exec(code, globals())
                st.success("✅ Executed successfully")
            except Exception as e:
                st.error(f"❌ Error in cell {i+1}:\n{e}")

    # Step 5: Show the output if defined
    if "submission" in globals():
        st.success("🎉 Output from the notebook:")
        st.write(submission)
        # Optionally, allow user to download the submission file
        csv = submission.to_csv(index=False)
        st.download_button("Download Submission", csv, file_name="submission.csv")
    else:
        st.warning("⚠️ 'submission' variable not found. Make sure your notebook defines it.")
else:
    st.info("⬆️ Please upload all required files to begin.")

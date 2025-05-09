import streamlit as st
import pandas as pd
import time
import io
from excel_generator import generate_product_details

st.title("Product Details Generator")

st.markdown("""
This app allows you to upload an Excel file with product details and then uses the OpenAI-powered function to generate detailed information for each product.  
The output is provided as a downloadable Excel file.
""")
st.markdown("""
Your spreadsheet should include these columns in the exact following sequence: Brand, Item number, Name, ID. With exact titles to each of these columns.
""")

# File uploader widget
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read the uploaded Excel file into a DataFrame
        df = pd.read_excel(uploaded_file)
        st.success("Excel file successfully uploaded and read!")
        st.write(f"Found **{len(df)}** products in your file.")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
    
    if st.button("Generate Product Details"):
        total_rows = len(df)
        st.info(f"Processing {total_rows} products. This may take a few moments...")
        
        # Prepare lists for storing the output
        internal_reference = []
        product_name = []
        specs = []
        ecom_desc = []
        disclaimer = []
        desc = []
        id2 = []

        progress_bar = st.progress(0)
        placeholder_1 = st.empty()
        placeholder_2 = st.empty()
        
        # Process each row in the DataFrame
        for index, row in df.iterrows():
            placeholder_2.write(f"Processing product {index + 1} of {total_rows}")
            # Retrieve input fields from the row
            brand = row.get("Brand", "")
            item_number = row.get("Item number", "")
            name = row.get("Name", "")
            id1 = row.get("ID", "")
            
            placeholder_1.write(f"Generating details for: **{item_number} - {name}**")
            details = generate_product_details(
                brand, item_number, name, id1
            )
            if details:
                internal_reference.append(details.get("Internal Reference", ""))
                product_name.append(details.get("Name", ""))
                specs.append(details.get("Specifications", ""))
                ecom_desc.append(details.get("eCommerce Description", ""))
                disclaimer.append(details.get("Disclaimer", ""))
                desc.append(details.get("Description", ""))
                id2.append(details.get("ID", ""))
                print("✓ Successfully generated details", "")
            else:
                st.warning(f"Failed to generate details for product {item_number}")
                # Append empty strings if generation failed
                internal_reference.append("")
                product_name.append("")
                specs.append("")
                ecom_desc.append("")
                disclaimer.append("")
                desc.append("")
                id2.append("")  
            progress_bar.progress((index + 1) / total_rows)
            time.sleep(1)  # Optional delay to avoid rate limiting

        st.info("Generating the output Excel file...")

        # Create a new DataFrame with the generated details
        new_df = pd.DataFrame({
            "Internal Reference": internal_reference,
            "Name": product_name,
            "Specifications": specs,
            "eCommerce Description": ecom_desc,
            "Disclaimer": disclaimer,
            "Description": desc,
            "ID": id2,
        })

        # Combine the original data with the generated details (if desired)
        combined_df = pd.concat([df, new_df], axis=1)

        # Write the combined DataFrame to an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            combined_df.to_excel(writer, index=False)
        output.seek(0)

        st.success("Processing complete!")
        st.download_button(
            label="Download Output Excel File",
            data=output,
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
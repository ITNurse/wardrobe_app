import streamlit as st
import pandas as pd
from PIL import Image
import os

# Paths to your files
metadata_file = r"Inventory.xlsx"
image_folder = r"C:\Users\lisat\OneDrive\008 Inventory\Apparel Images"

# Load your metadata from Excel
sheet_name = "Apparel Acces Footwear Inv"
df = pd.read_excel(metadata_file, sheet_name=sheet_name)

# Streamlit app setup
st.title("My Wardrobe Viewer")

# Sidebar filter for category
categories = df['Category'].dropna().unique()  # Handle missing values if present
selected_category = st.sidebar.selectbox("Select Category", sorted(categories))

# Filter data by selected category
filtered_df = df[df['Category'] == selected_category]

# Display filtered items
st.write(f"Showing items for: **{selected_category}**")
for _, row in filtered_df.iterrows():
    item_id = row['Item ID']
    image_path = os.path.join(image_folder, f"{item_id}.jpg")  # Adjust if images are in different format

    # Display image if it exists
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption=row.get('Brand', 'Unknown'), use_container_width=True)

    # Display metadata
    st.write(f"**Item ID:** {row['Item ID']}")
    st.write(f"**Category:** {row['Category']}")
    st.write(f"**Brand:** {row['Brand']}")
    st.write(f"**Color:** {row['Color']}")
    st.write(f"**Size:** {row['Size']}")
    st.write(f"**Quantity:** {row['Quant']}")
    st.write(f"**Condition:** {row['Condition']}")
    st.write(f"**Purchase Date:** {row['Purchase Date']}")
    st.write(f"**Purchase Price:** {row['Purchase Price']}")
    st.write(f"**Notes:** {row['Notes']}")
    st.write(f"**Sell Price:** {row['Sell Price']}")
    st.write("---")

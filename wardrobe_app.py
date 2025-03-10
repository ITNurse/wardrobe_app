import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64
import io  # Import the io module for BytesIO
from datetime import datetime

__version__ = "1.1.3"

# Paths to your files
metadata_file = r"C:\Users\lisat\OneDrive\008 Inventory\Inventory.xlsx"
image_folder = r"C:\Users\lisat\OneDrive\008 Inventory\Apparel Images"

# Load your metadata from Excel
sheet_name = "Apparel Acces Footwear Inv"
df = pd.read_excel(metadata_file, sheet_name=sheet_name)

# Streamlit app setup
st.title("My Wardrobe Viewer")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "grid"
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

# Fixed thumbnail height
thumbnail_height = 150

def get_image_base64(image_path, height):
    """
    Load an image, resize it to the specified height while maintaining aspect ratio,
    and return the base64-encoded string for embedding in HTML.
    """
    with Image.open(image_path) as img:
        aspect_ratio = img.width / img.height
        width = int(height * aspect_ratio)
        img = img.resize((width, height))
        # Encode the image to base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return img_base64

def preprocess_data(df):
    """
    Add a new column 'Category Group' that contains the substring before the hyphen in the 'Category' field.
    Ensure the 'Size' column is converted to string for consistent filtering and sorting.
    """
    df['Category Group'] = df['Category'].str.split('-').str[0].str.strip()  # Extract substring before hyphen
    df['Size'] = df['Size'].astype(str)  # Convert 'Size' column to string
    return df

# Preprocess the DataFrame to create the 'Category Group' column and fix 'Size'
df = preprocess_data(df)

def show_grid():
    """
    Display the grid of items with category group and size filters, applied only after clicking 'Go'.
    """
    st.sidebar.title("Filters")

    # Add default options to the filters
    category_groups = ['Select a Group'] + sorted(df['Category Group'].dropna().unique())
    sizes = ['Select a Size'] + sorted(df['Size'].dropna().unique())

    # Initialize session state for filter values
    if "temp_category_group" not in st.session_state:
        st.session_state["temp_category_group"] = "Select a Group"
    if "temp_size" not in st.session_state:
        st.session_state["temp_size"] = "Select a Size"
    if "applied_category_group" not in st.session_state:
        st.session_state["applied_category_group"] = "Select a Group"
    if "applied_size" not in st.session_state:
        st.session_state["applied_size"] = "Select a Size"

    # Create temporary dropdown filters
    st.session_state["temp_category_group"] = st.sidebar.selectbox(
        "Select Category Group", category_groups, index=category_groups.index(st.session_state["temp_category_group"])
    )
    st.session_state["temp_size"] = st.sidebar.selectbox(
        "Select Size", sizes, index=sizes.index(st.session_state["temp_size"])
    )

    # Add a 'Go' button to apply filters
    if st.sidebar.button("Go"):
        st.session_state["applied_category_group"] = st.session_state["temp_category_group"]
        st.session_state["applied_size"] = st.session_state["temp_size"]

    # Filter the DataFrame based on the applied filters
    applied_category_group = st.session_state["applied_category_group"]
    applied_size = st.session_state["applied_size"]

    if applied_category_group != "Select a Group" and applied_size != "Select a Size":
        filtered_df = df[(df["Category Group"] == applied_category_group) & (df["Size"] == applied_size)]
        st.write(f"Showing items for: **{applied_category_group}** and **Size: {applied_size}**")
    elif applied_category_group != "Select a Group":
        filtered_df = df[df["Category Group"] == applied_category_group]
        st.write(f"Showing items for: **{applied_category_group}**")
    elif applied_size != "Select a Size":
        filtered_df = df[df["Size"] == applied_size]
        st.write(f"Showing items for: **Size: {applied_size}**")
    else:
        filtered_df = df
        st.write("Showing all items.")

    # Display filtered items in a grid layout
    items_per_row = 4
    rows = [filtered_df.iloc[i:i+items_per_row] for i in range(0, len(filtered_df), items_per_row)]

    for row in rows:
        cols = st.columns(items_per_row)  # Create new columns for the row
        for col, (_, item) in zip(cols, row.iterrows()):
            item_id = item["Item ID"]
            image_path = os.path.join(image_folder, f"{item_id}.jpg")  # Adjust if images are in different format
            brand = item.get("Brand", "")  # Get "Brand" field, fallback to empty if missing
            size = item.get("Size", "")    # Get "Size" field, fallback to empty if missing
            status = item.get("Item Status", "")    # Get "Item Status" field, fallback to empty if missing

            if os.path.exists(image_path):
                # Encode the image to base64
                img_base64 = get_image_base64(image_path, thumbnail_height)

                # Display the image, brand, size, and a form for selection
                with col:
                    with st.form(key=f"form_{item_id}"):
                        # Display the image
                        image_html = f"""
                            <img src="data:image/jpeg;base64,{img_base64}" style="height:{thumbnail_height}px; border-radius: 5px; border: 1px solid #ccc;" />
                        """
                        st.markdown(image_html, unsafe_allow_html=True)

                        # Display brand, size, and status in 8pt font
                        st.markdown(f"""
                            <p style="font-size:10pt; margin:0;">{brand}</p>
                            <p style="font-size:8pt; margin:0;">Size: {size}</p>
                            <p style="font-size:8pt; margin:0;">Status: {status}</p>
                        """, unsafe_allow_html=True)

                        # Submit button for selection
                        if st.form_submit_button("Details"):
                            st.session_state.page = "details"
                            st.session_state.selected_item = item_id
                            st.rerun()


def show_details(item_id):
    """
    Display the details of a specific item.
    """
    item = df[df['Item ID'] == item_id].iloc[0]
    st.write(f"### Details for Item ID: {item_id}")
    
    # Display the item's image
    image_path = os.path.join(image_folder, f"{item_id}.jpg")
    if os.path.exists(image_path):
        with Image.open(image_path) as img:
            st.image(img, caption=item['Category'], use_container_width=True)

    # Display all metadata
    st.write("#### Item Details:")
    for col in df.columns:
        value = item[col]

        # Check if the column is a datetime column and format it as a date
        if isinstance(value, pd.Timestamp):
            formatted_value = value.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
        else:
            formatted_value = value

        st.write(f"**{col}:** {formatted_value}")

    # Back button to return to the grid
    if st.button("Back"):
        st.session_state.page = "grid"
        st.rerun()

# Handle navigation between grid and details view
if st.session_state.page == "grid":
    show_grid()
elif st.session_state.page == "details":
    show_details(st.session_state.selected_item)

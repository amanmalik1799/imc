import streamlit as st
from PIL import Image
import io

st.title("🖼️ Image Format Converter & Resizer")

# File upload section
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    try:
        # Display original image information
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_column_width=True)
        st.write(f"Original Format: {uploaded_file.type.split('/')[-1].upper()}")
        st.write(f"Original Dimensions: {image.size[0]}x{image.size[1]} pixels")
    except Exception as e:
        st.error(f"Error loading image: {e}")
        st.stop()

# Conversion settings
target_format = st.selectbox("Select target format", ["JPEG", "PNG", "WebP"]).lower()
resize_option = st.radio("Resize options:", ("Original Size", "Custom Dimensions", "Scale Percentage"))

# Resize parameters
new_width, new_height = None, None
scale_percent = 100

if resize_option == "Custom Dimensions":
    if uploaded_file:
        new_width = st.number_input("Width (pixels)", min_value=1, value=image.size[0])
        new_height = st.number_input("Height (pixels)", min_value=1, value=image.size[1])
elif resize_option == "Scale Percentage":
    scale_percent = st.number_input("Scale percentage", min_value=1, max_value=500, value=100)

# File size management
max_size_option = st.checkbox("Set maximum file size")
max_size_bytes = None
if max_size_option:
    max_size_mb = st.number_input("Maximum file size (MB)", min_value=0.1, value=1.0, step=0.1)
    max_size_bytes = max_size_mb * 1024 * 1024

if st.button("Process and Download"):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            
            # Handle transparency for JPEG format
            if target_format in ["jpeg", "jpg"] and image.mode in ['RGBA', 'LA']:
                image = image.convert('RGB')
            
            # Resize image based on user selection
            if resize_option == "Custom Dimensions":
                image = image.resize((new_width, new_height))
            elif resize_option == "Scale Percentage":
                width, height = image.size
                new_width = int(width * scale_percent / 100)
                new_height = int(height * scale_percent / 100)
                image = image.resize((new_width, new_height))

            # Initialize conversion parameters
            img_buffer = io.BytesIO()
            params = {'format': target_format}
            
            # Set format-specific parameters
            if target_format in ["jpeg", "jpg"]:
                params['quality'] = 95  # Start with high quality
            elif target_format == "png":
                params['compress_level'] = 9  # Max compression
            elif target_format == "webp":
                params['quality'] = 80

            # Initial save to check size
            image.save(img_buffer, **params)
            current_size = img_buffer.tell()

            # Optimize file size if needed
            if max_size_bytes and current_size > max_size_bytes:
                if target_format in ["jpeg", "jpg", "webp"]:
                    quality_param = 'quality'
                    min_quality = 10 if target_format == "webp" else 5
                    current_quality = params.get(quality_param, 95)
                    
                    while current_quality >= min_quality and current_size > max_size_bytes:
                        current_quality -= 5
                        img_buffer = io.BytesIO()
                        image.save(img_buffer, format=target_format, **{quality_param: current_quality})
                        current_size = img_buffer.tell()
                    
                    if current_quality < min_quality:
                        st.warning("Reached minimum quality settings. File size might still exceed limit.")
                elif target_format == "png":
                    st.warning("PNG uses maximum compression. Further size reduction requires resizing.")

            # Prepare download
            img_buffer.seek(0)
            st.success(f"Processing complete! Final size: {current_size/1024:.2f} KB")
            
            st.download_button(
                label="Download Processed Image",
                data=img_buffer,
                file_name=f"processed_image.{target_format}",
                mime=f"image/{target_format}"
            )
            
        except Exception as e:
            st.error(f"Processing error: {e}")
    else:
        st.warning("Please upload an image first!")
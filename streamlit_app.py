import streamlit as st
from PIL import Image
import pandas as pd
import requests
from io import BytesIO
import io
import zipfile

class ImageAnalyzer:
    def __init__(self, image_input, tolerance=10):
        # Check if input is a path or a file-like object
        if isinstance(image_input, str):  # File path
            self.image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):  # Pillow Image object
            self.image = image_input.convert("RGB")
        else:  # File-like object (e.g., BytesIO)
            self.image = Image.open(image_input).convert("RGB")
        
        self.pixels = self.image.load()
        self.width, self.height = self.image.size
        self.tolerance = tolerance


    def is_almost_white(self, pixel):
        return all(255 - value <= self.tolerance for value in pixel)

    def is_almost_black(self, pixel):
        return all(value <= self.tolerance for value in pixel)

    def find_leftmost_nonwhite(self):
        for x in range(self.width):
            for y in range(self.height):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return x
        return -1

    def find_uppermost_nonwhite(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return y
        return -1

    def find_rightmost_nonwhite(self):
        for x in range(self.width - 1, -1, -1):
            for y in range(self.height):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return x
        return -1

    def find_downmost_nonwhite(self):
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                if not self.is_almost_white(self.pixels[x, y]):  # Check using the tolerance
                    return y
        return -1
    # ==================================
    # def find_leftmost_nonblack(self):
    #     for x in range(self.width):
    #         for y in range(self.height):
    #               if not self.is_almost_black(self.pixels[x, y]):
    #                 return x
    #     return -1

    # def find_uppermost_nonblack(self):
    #     for y in range(self.height):
    #         for x in range(self.width):
    #             if not self.is_almost_black(self.pixels[x, y]):  # Check using the tolerance
    #                 return y
    #     return -1

    # def find_rightmost_nonblack(self):
    #     for x in range(self.width - 1, -1, -1):
    #         for y in range(self.height):
    #             if not self.is_almost_black(self.pixels[x, y]):  # Check using the tolerance
    #                 return x
    #     return -1

    # def find_downmost_nonblack(self):
    #     for y in range(self.height - 1, -1, -1):
    #         for x in range(self.width):
    #             if not self.is_almost_black(self.pixels[x, y]):  # Check using the tolerance
    #                 return y
    #     return -1
    # ==================================
    def find_rim(self,image_input):
        a = ImageAnalyzer(image_input)
        leftmost_x = a.find_leftmost_nonwhite()
        uppermost_y = a.find_uppermost_nonwhite()
        rightmost_x = a.find_rightmost_nonwhite()
        downmost_y = a.find_downmost_nonwhite()
        # return leftmost_x
        return leftmost_x,uppermost_y,rightmost_x,downmost_y

    def paste_image(self, overlay_image, coordinates=(0, 0)):
        overlay_image = overlay_image.convert("RGBA")
        if coordinates[0] + overlay_image.width > self.image.width or coordinates[1] + overlay_image.height > self.image.height:
            raise ValueError("Overlay image goes beyond the base image dimensions.")
        self.image.paste(overlay_image, coordinates, overlay_image)
        return self.image

    def layout_images(self, image_paths, layout="horizontal"):
        images = [Image.open(path).convert("RGB") for path in image_paths]
        widths, heights = zip(*(img.size for img in images))

        if layout == "horizontal":
            total_width = sum(widths)
            max_height = max(heights)
            new_img = Image.new("RGB", (total_width, max_height), (255, 255, 255))
            x_offset = 0
            for img in images:
                new_img.paste(img, (x_offset, 0))
                x_offset += img.width
        elif layout == "vertical":
            total_height = sum(heights)
            max_width = max(widths)
            new_img = Image.new("RGB", (max_width, total_height), (255, 255, 255))
            y_offset = 0
            for img in images:
                new_img.paste(img, (0, y_offset))
                y_offset += img.height
        else:
            raise ValueError("Invalid layout type. Choose 'horizontal' or 'vertical'.")

        return new_img

    def merge_images(self, image1_path, image2_path, alpha=0.5):
        img1 = Image.open(image1_path).convert("RGBA")
        img2 = Image.open(image2_path).convert("RGBA")
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)
        return Image.blend(img1, img2, alpha)

    def crop(self, left, upper, right, lower):
        # Validate crop dimensions
        if left < 0 or upper < 0 or right > self.width or lower > self.height:
            raise ValueError("Crop coordinates are out of image bounds.")
        if left >= right or upper >= lower:
            raise ValueError("Invalid crop dimensions. Ensure left < right and upper < lower.")
        
        # Perform the cropping
        cropped_image = self.image.crop((left, upper, right, lower))
        return cropped_image
    def resize_with_aspect_ratio(self, new_width=None, new_height=None):
        if new_width is None and new_height is None:
            raise ValueError("At least one of new_width or new_height must be specified.")

        # Calculate the aspect ratio of the image
        aspect_ratio = self.width / self.height

        if new_width is not None:
            # Calculate new height while maintaining aspect ratio
            new_height = int(new_width / aspect_ratio)
        elif new_height is not None:
            # Calculate new width while maintaining aspect ratio
            new_width = int(new_height * aspect_ratio)

        # Resize the image
        resized_image = self.image.resize((new_width, new_height))
        return resized_image


def importfromGit(image_url):

    # Send a GET request to fetch the raw image
    response = requests.get(image_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open the image from the response content
        img = Image.open(BytesIO(response.content))
        return img
    else:
        return print("Failed to retrieve the image. Status code:", response.status_code)

def Edit_001(main_input, platform, type_product,advanced_setting,adv_buffer1=None,adv_buffer2=None):
    product_input = ImageAnalyzer(main_input)

    # Select platform and buffer data
    if platform == "LD":
        background_input = ImageAnalyzer(importfromGit("https://raw.githubusercontent.com/Nanotez001/image_editor/refs/heads/main/asset/temp/Temp_525x338.jpg"))
        background_size = [525, 338]
        buffer = pd.read_csv("https://raw.githubusercontent.com/Nanotez001/image_editor/refs/heads/main/asset/buffer/LD_buffer.csv")
    elif platform == "JJT":
        background_input = ImageAnalyzer(importfromGit("https://raw.githubusercontent.com/Nanotez001/image_editor/refs/heads/main/asset/temp/Temp_1000x1000.jpg"))
        background_size = [1000, 1000]
        buffer = pd.read_csv("https://raw.githubusercontent.com/Nanotez001/image_editor/refs/heads/main/asset/buffer/JJT_buffer.csv")

    # Get non-white pixel boundaries
    leftmost_x = product_input.find_leftmost_nonwhite()
    uppermost_y = product_input.find_uppermost_nonwhite()
    rightmost_x = product_input.find_rightmost_nonwhite()
    downmost_y = product_input.find_downmost_nonwhite()

    # st.write("CHECK1")
    # # Paths for intermediate files
    # cropped_path = "C:/Users/LEGION by Lenovo/Documents/GitHub/image_editor/asset/storage/Cropped_Test.jpg"
    # resized_path = "C:/Users/LEGION by Lenovo/Desktop/Image_Editor/Resized_Test.jpg"
    # Crop and save the image
    cropped_image = product_input.crop(leftmost_x, uppermost_y, rightmost_x, downmost_y)
    # cropped_image.save(cropped_path)

    # st.write("CHECK2")
    # st.write(buffer.loc[buffer['product'] == type_product,'buffer2'].values[0])
    # st.write(buffer)
    if advanced_setting:
        buffer1 = adv_buffer1
        buffer2 = adv_buffer2
        # Resize the cropped image
        resized_image = ImageAnalyzer(cropped_image).resize_with_aspect_ratio(new_height=int(buffer2))
        # resized_image.save(resized_path)
        # st.write("CHECK3")
        # Overlay the resized image onto the background
        background = background_input
        result = background.paste_image(resized_image, coordinates=((background_size[0] - resized_image.width) // 2,int(buffer1)))
        return result
    else:
        buffer1 = buffer.loc[buffer['product'] == type_product,'buffer1'].values[0] 
        buffer2 = buffer.loc[buffer['product'] == type_product,'buffer2'].values[0]
        # Resize the cropped image
        resized_image = ImageAnalyzer(cropped_image).resize_with_aspect_ratio(new_height=int(buffer2))
        # resized_image.save(resized_path)
        # st.write("CHECK3")
        # Overlay the resized image onto the background
        background = background_input
        result = background.paste_image(resized_image, coordinates=((background_size[0] - resized_image.width) // 2,int(buffer1)))
        return result

# ====================================
def main():
    st.title("IMAGE JUNCTION Batch v0.1")

    # Sidebar components
    st.sidebar.title("Select Options")
    load = st.sidebar.selectbox("Load:", ["J-001", "J-002"])
    st.sidebar.write("=== LD ========================")
    Item_checkbox = st.sidebar.checkbox("LD_logo")


# =======================================================================
    # File uploader
    uploaded_files = st.file_uploader("Upload Files (คำแนะนำ แก้ไขชื่อไฟล์ให้เรียบร้อยก่อน)", type=["jpg", "jpeg","png"], accept_multiple_files=True)
    col1, col2, col3, col4 = st.columns(4)

    # Add text inputs to each column
    with col1:
        size = st.text_input("",placeholder="Size")

    with col2:
        x_axis = st.text_input("",placeholder="X_axis")

    with col3:
        y_axis = st.text_input("",placeholder="Y_axis")

    st.write(load,size,x_axis,y_axis)
# if uploaded_files:
    # Process each uploaded file
    result_images=[]
    original_name=[]
    for uploaded_file in uploaded_files:
        try:
            # Save the original file name
            original_name.append(uploaded_file.name)

            # Open and convert the uploaded image
            png_image = Image.open(uploaded_file).convert("RGBA")

            # Create a white background image
            white_background = Image.new("RGB", png_image.size, (255, 255, 255))

            # Combine the PNG with the white background (handle transparency)
            white_background.paste(png_image, mask=png_image.split()[3])

            # Process the result
            result = Edit_001(white_background, platform, type_product, advanced_setting, adv_buffer1, adv_buffer2)

            # Append the result to the results list
            result_images.append(result)

        except Exception as e:
            st.error(f"Error processing the image '{uploaded_file.name}': {e}")

            # result_images.append(result)
        # Display the before and after images
        col1, col2 = st.columns(2)
        with col1:
            st.image(white_background, caption="Before", use_container_width=True)

        with col2:
            # result_image_path = "C:/Users/LEGION by Lenovo/Desktop/Image_Editor/Result_Test.jpg"
            st.image(result, caption="After", use_container_width=True)
    # save_folder_path = st.text_input(label="Enter your FOLDER address:",placeholder="EX. C:\\Users\\LEGION by Lenovo\\Desktop\\Result\\ ")
    # if st.button(label = "save"): 
    #     i=0
    #     for image in result_images:
    #         save_path = f"{save_folder_path}/{original_name[i]}"
    #         i+=1     
    #         image.save(save_path)

        # Download button to download the image
    if result_images:
        # Create a BytesIO object for the ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, image in enumerate(result_images):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG")
                img_bytes.seek(0)
                if platform == "LD":
                    zip_file.writestr(f"{original_name[i]}_LuckyDigital.jpg", img_bytes.read())
                elif platform == "JJT":
                    zip_file.writestr(f"{original_name[i]}_Jingjungto.jpg", img_bytes.read())

        zip_buffer.seek(0)
        
        # Add a single download button for all images as a ZIP file
        st.download_button(
            label="Download All Images as ZIP",
            data=zip_buffer,
            file_name="Result_Images.zip",
            mime="application/zip",
        )
    else:
        st.info("Please upload at least one image to proceed.")

# Run the app
if __name__ == "__main__":
    main()

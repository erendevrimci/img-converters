import cv2
import numpy as np
import potrace
import svgwrite
import os
from PIL import Image

def convert_single_file(image_file, svg_file):
    """Convert a single image file to SVG format."""
    try:
        with Image.open(image_file) as pil_img:
            img = np.array(pil_img.convert('L'))
    except Exception as e:
        print(f"Error reading {image_file}: {str(e)}")
        return

    # Threshold the image
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # Create a bitmap from the array
    bmp = potrace.Bitmap(thresh)

    # Trace the bitmap to a path
    path = bmp.trace()

    # Create an SVG drawing
    dwg = svgwrite.Drawing(svg_file, profile='tiny')
    for curve in path:
        svg_path = dwg.path(d="M {} {}".format(curve.start_point[0], curve.start_point[1]), fill="black")
        for segment in curve:
            if segment.is_corner:
                svg_path.push("L {} {}".format(segment.c[0], segment.c[1]))
            else:
                svg_path.push("C {} {} {} {}".format(segment.c1[0], segment.c1[1], segment.c2[0], segment.c2[1], segment.end_point[0], segment.end_point[1]))
        dwg.add(svg_path)

    # Save the SVG file
    dwg.save()
    print(f"Conversion complete. SVG file saved as {svg_file}")

def image_to_svg(input_path, output_path):
    """Convert images in a file or directory to SVG format."""
    print(f"Input Path: {input_path}")
    print(f"Output Path: {output_path}")

    if os.path.isfile(input_path):
        if input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            svg_file = os.path.splitext(output_path)[0] + '.svg'
            convert_single_file(input_path, svg_file)
        else:
            print(f"Skipping {input_path}: Not a supported image file")
    elif os.path.isdir(input_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for filename in os.listdir(input_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                image_file = os.path.join(input_path, filename)
                svg_file = os.path.join(output_path, os.path.splitext(filename)[0] + '.svg')
                convert_single_file(image_file, svg_file)
    else:
        print("Invalid input path. Please provide a supported image file or a directory containing image files.")

if __name__ == "__main__":
    # Example usage:
    # image_to_svg('input.jpg', 'output.svg')  # For single file
    # image_to_svg('input_folder', 'output_folder')  # For batch processing

    # Example paths (update these paths as needed)
    input_path = '/path/to/input'
    output_path = '/path/to/output'
    image_to_svg(input_path, output_path)

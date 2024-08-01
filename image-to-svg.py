import cv2
import numpy as np
import potrace
from svgwrite import Path, Line, CubicBezier
import os
from PIL import Image

def image_to_svg(input_path, output_path):
    print(f"Input Path: {input_path}")
    print(f"Output Path: {output_path}")

    def convert_single_file(image_file, svg_file):
        # Read the image file
        img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            # If cv2 fails to read (e.g., for WebP), try with PIL
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
        svg_paths = []
        for curve in path:
            svg_path = Path()
            svg_path.append(Line(curve.start_point, curve.start_point))
            for segment in curve:
                if segment.is_corner:
                    svg_path.append(Line(segment.c, segment.end_point))
                else:
                    svg_path.append(CubicBezier(segment.c1, segment.c2, segment.end_point, segment.end_point))
            svg_paths.append(svg_path.d())
        
        # Write the SVG file
        with open(svg_file, 'w') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}">\n'.format(img.shape[1], img.shape[0]))
            for path in svg_paths:
                f.write('  <path d="{}" fill="black" />\n'.format(path))
            f.write('</svg>\n')

        print(f"Conversion complete. SVG file saved as {svg_file}")

    # Check if the input is a file or a directory
    if os.path.isfile(input_path):
        # If it's a file, convert it directly
        if input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            svg_file = os.path.splitext(output_path)[0] + '.svg'
            convert_single_file(input_path, svg_file)
        else:
            print(f"Skipping {input_path}: Not a supported image file")
    elif os.path.isdir(input_path):
        # If it's a directory, process all supported image files in it
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for filename in os.listdir(input_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                image_file = os.path.join(input_path, filename)
                svg_file = os.path.join(output_path, os.path.splitext(filename)[0] + '.svg')
                convert_single_file(image_file, svg_file)
    else:
        print("Invalid input path. Please provide a supported image file or a directory containing image files.")

# Example usage:
#image_to_svg('input.jpg', 'output.svg')  # For single file
#image_to_svg('input_folder', 'output_folder')  # For batch processing

#image_to_svg('/Users/imac/Desktop/ustad-ai-accountant/ui/ustad-ideogram/a2svg', '/Users/imac/Desktop/ustad-ai-accountant/ui/ustad-ideogram/asvg')
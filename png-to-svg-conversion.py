import cv2
import numpy as np
import potrace
from svgwrite import Path, Line, CubicBezier

def png_to_svg(png_file, svg_file):
    # Read the PNG file
    img = cv2.imread(png_file, cv2.IMREAD_GRAYSCALE)
    
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

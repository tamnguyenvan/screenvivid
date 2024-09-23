import os
import glob
from PIL import Image

image_dir = 'C:/Users/tamva/Downloads/1-aero_busy'

state = 'wait'
output_dir = '.'
os.makedirs(output_dir, exist_ok=True)

image_paths = sorted(glob.glob(os.path.join(image_dir, '*.png')))
base_size = 32
scales = [0.75, 1, 1.5, 2, 3]
for i, path in enumerate(image_paths):
    image = Image.open(path)

    for scale in scales:
        outdir = os.path.join(output_dir, str(scale) + 'x', state)
        if not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        output_path = os.path.join(outdir,  f'{state}_{i+1}.png')
        new_width, new_height = int(scale * base_size), int(scale * base_size)

        resized_image = image.copy()
        if new_width != image.size[0] or new_height != image.size[1]:
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        resized_image.save(output_path)
        print(output_path)
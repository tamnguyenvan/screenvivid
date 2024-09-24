import os
import glob
import cv2
from PIL import Image


def main():
    input_dir = "cursor_images"
    states = os.listdir(input_dir)

    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)

    base_size = 32
    scales = [1, 1.5, 2, 3]

    for scale in scales:
        outdir = os.path.join(output_dir, f"{scale}x")
        if not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)

    for state in states:
        cursor_state_dir = os.path.join(input_dir, state)

        filenames = os.listdir(cursor_state_dir)
        for filename in filenames:
            input_path = os.path.join(cursor_state_dir, filename)
            img = Image.open(input_path)
            img_w, img_h = img.size

            if img_w / base_size in scales:
                scale = img_w / base_size
                scale_str = f"{int(scale)}x" if scale.is_integer() else f"{scale:.1f}x"
                output_path = os.path.join(output_dir, scale_str, f"{state}.png")
                print(output_path)
                img.save(output_path)


if __name__ == "__main__":
    main()
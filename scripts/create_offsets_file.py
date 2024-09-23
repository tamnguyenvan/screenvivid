import struct
import argparse
import json
import os

def read_cur_hotspots(cur_file):
    with open(cur_file, 'rb') as f:
        # Read header of .cur file
        f.seek(0)
        reserved, image_type, num_images = struct.unpack('<HHH', f.read(6))
        hotspots = []

        for i in range(num_images):
            # Read image info
            f.seek(6 + i * 16)
            width, height, color_count, reserved, x_hot, y_hot, bytes_in_res, image_offset = struct.unpack('<BBBBHHII', f.read(16))
            hotspots.append([(width, height), (x_hot, y_hot)])

    return hotspots

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cursor_dir", type=str, help="Path to the directory contains .cur and .ani files")
    parser.add_argument("--output", type=str, default=".", help="Output path")
    args = parser.parse_args()

    # "windows": [
    #     "arrow", "ibeam", "wait", "cross", "uparrow", "sizenwse", "sizenesw",
    #     "sizewe", "sizens", "sizeall", "no", "hand", "appstarting", "help"
    # ],
    cursors_map = {
        "aero_arrow_l.cur": "arrow",
        "beam_rl.cur": "ibeam",
        "cross_rl.cur": "cross",
        "aero_up_l.cur": "uparrow",
        "aero_nwse_l.cur": "sizenwse",
        "aero_nesw_l.cur": "sizenesw",
        "aero_ew_l.cur": "sizewe",
        "aero_ns_l.cur": "sizens",
        "aero_move_l.cur": "sizeall",
        "aero_unavail_l.cur": "no",
        "aero_link_l.cur": "hand",
        "aero_helpsel_l.cur": "help"
    }

    cur_dir = args.cursor_dir
    output_file = os.path.join(args.output, "offsets.json")

    base_size = 32
    scales = [0.75, 1, 1.5, 2, 3]
    sizes = [int(scale * base_size) for scale in scales]
    output = {}
    for cur_file, cursor_name in cursors_map.items():
        output[cursor_name] = {}
        cur_file = os.path.join(cur_dir, cur_file)
        hotspots = read_cur_hotspots(cur_file)
        for i, cursor_info in enumerate(hotspots):
            (width, height), (x_hot, y_hot) = cursor_info
            if width in sizes:
                scale = scales[sizes.index(width)]
                scale_str = str(scale) + "x"
                print(cursor_name, width, height, x_hot, y_hot)
                output[cursor_name][scale_str] = [x_hot, y_hot]

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Save output as {output_file}")
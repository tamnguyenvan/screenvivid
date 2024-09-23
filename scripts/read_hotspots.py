import struct

def read_ani_hotspot(ani_file):
    with open(ani_file, 'rb') as f:
        data = f.read()

        # Find LIST chunk
        if b'LIST' not in data:
            raise ValueError("Invalid .ani file: LIST chunk not found")

        # Start position of LIST chunk
        list_start = data.index(b'LIST')

        # Skip header RIFF/ACON to get CURS chunk
        idx = list_start + 12  # Skip 'LIST' (4 bytes) and size (4 bytes) and 'ACON' (4 bytes)

        # Find start position of CURS chunk
        while idx < len(data):
            chunk_id = data[idx:idx + 4]
            chunk_size = struct.unpack('<I', data[idx + 4:idx + 8])[0]
            if chunk_id == b'icon':
                # Read CURS chunk
                cursor_data = data[idx + 8: idx + 8 + chunk_size]
                x_hotspot, y_hotspot = struct.unpack('<HH', cursor_data[10:14])
                return x_hotspot, y_hotspot

            idx += 8 + chunk_size

    raise ValueError("No cursor found in .ani file")


if __name__ == "__main__":
    ani_file = "C:/Windows/Cursors/aero_working.ani"
    try:
        x_hot, y_hot = read_ani_hotspot(ani_file)
        print(f"Hotspot of the first image: x={x_hot}, y={y_hot}")
    except ValueError as e:
        print(f"Error: {e}")

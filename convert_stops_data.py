import json
import gzip
import base64
import argparse
import os
from datetime import datetime

def process_transit_data(input_path):
    # 1. Load Original Data
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON: {e}")
            return

    # 2. Minimize Structure: Array of Arrays [name_tc, name_en, lat, lng]
    # This strips repetitive keys to save significant space
    minimized_data = {}
    for operator, stops in data.items():
        minimized_data[operator] = [
            [
                stop.get('name_tc', ''),
                stop.get('name_en', ''),
                round(stop.get('lat', 0), 6),
                round(stop.get('lng', 0), 6)
            ]
            for stop in stops
        ]

    # 3. Convert to UTF-8 String and Gzip
    json_str = json.dumps(minimized_data, ensure_ascii=False)
    encoded_bytes = json_str.encode('utf-8')
    compressed = gzip.compress(encoded_bytes)

    # 4. Base64 Encode
    b64_string = base64.b64encode(compressed).decode('utf-8')

    # 5. Verification Step (Decode back to check integrity)
    decoded_b64 = base64.b64decode(b64_string)
    decompressed = gzip.decompress(decoded_b64)
    verified_data = json.loads(decompressed.decode('utf-8'))

    if verified_data == minimized_data:
        print("✅ Integrity Check Passed: Decompressed data matches minimized source.")
    else:
        print("❌ Integrity Check Failed: Data corruption detected.")
        return

    # 6. Final Output
    date_str = datetime.now().strftime("%m%d") # e.g., 0327
    output_filename = f"HK_transit_{date_str}_data.txt"

    with open(output_filename, "w") as f:
        f.write(b64_string)

    print(f"--- Statistics ---")
    print(f"Original JSON:   {len(encoded_bytes)/1024:.2f} KB")
    print(f"Compressed B64:  {len(b64_string)/1024:.2f} KB (Reduced by ~{100 - (len(b64_string)/len(encoded_bytes)*100):.1f}%)")
    print(f"Result saved to: {output_filename}")
    print(f"\nCopy the contents of {output_filename} into your HTML 'BUS_DATA_COMPRESSED' variable.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress HK Transit JSON for HTML embedding.")
    parser.add_argument("file_path", help="Path to the stops_by_operator.json file")
    args = parser.parse_args()

    process_transit_data(args.file_path)

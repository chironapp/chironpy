import sys
from chironpy import read_file

def main(file_path):
    """
    Load and process a .fit file using chironpy.

    Args:
        file_path (str): Path to the .fit file.
    """
    try:
        print(f"Loading .fit file: {file_path}")
        # Replace `fit_parser.load` with the actual function in chironpy for loading .fit files
        data = read_file(file_path)
        print("File loaded successfully!")
        print(f"Summary: {data}")  # Replace with actual method to summarize the data
    except Exception as e:
        print(f"Error loading .fit file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_fit_file.py <path_to_fit_file>")
    else:
        main(sys.argv[1])
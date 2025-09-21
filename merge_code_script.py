import os

OUTPUT_FILE = "combined_output.py"
SRC_FOLDER = "src"
MAIN_FILE = "main.py"


def write_file_contents(out_f, file_path):
    """Write file header + contents to output file."""
    out_f.write(f"\n\n# ===== File: {file_path} =====\n\n")
    with open(file_path, "r", encoding="utf-8") as f:
        out_f.write(f.read())
        out_f.write("\n")  # Ensure newline at end


def collect_files(src_folder):
    """Recursively collect all .py files inside src/."""
    python_files = []
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return sorted(python_files)  # sort for consistency


def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        # Write main.py first
        if os.path.exists(MAIN_FILE):
            write_file_contents(out_f, MAIN_FILE)

        # Write all src/**/*.py files
        for py_file in collect_files(SRC_FOLDER):
            write_file_contents(out_f, py_file)

    print(f"✅ Combined file created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

import os
import csv

def fix_file(file_path):
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove any BOM if present
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # Split into lines and clean
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    # Write back with standardized format
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for line in lines:
            # Split on tab and clean each field
            fields = [field.strip() for field in line.split('\t')]
            if len(fields) >= 3:  # Only write valid rows
                writer.writerow(fields[:3])  # Only take first 3 fields

def main():
    base_dir = os.path.join('static', 'data', 'vocab')
    for level in range(1, 7):
        file_path = os.path.join(base_dir, f'hsk{level}_vocab.csv')
        if os.path.exists(file_path):
            print(f'Processing {file_path}...')
            fix_file(file_path)
            print(f'Finished processing {file_path}')

if __name__ == '__main__':
    main() 
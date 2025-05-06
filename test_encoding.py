import os
import csv

base_dir = os.path.join('static', 'data', 'vocab')

for level in range(1, 7):
    file_path = os.path.join(base_dir, f'hsk{level}_vocab.csv')
    print(f"\nChecking HSK{level} file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            count = 0
            for row in reader:
                count += 1
                if len(row) < 3:
                    print(f"Row {count} has incorrect format: {row}")
            print(f"Total rows read: {count}")
    except Exception as e:
        print(f"Error reading file: {str(e)}") 
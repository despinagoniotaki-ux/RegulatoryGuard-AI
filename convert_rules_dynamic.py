import csv
import json
import sys
import os

def convert_csv_to_json(input_csv, output_json="regulatory_rules.json"):
    if not os.path.exists(input_csv):
        print(f"Error: Could not find '{input_csv}'.")
        return
        
    try:
        with open(input_csv, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            
            rules_list = []
            for row in reader:
                processed_row = {}
                for key, value in row.items():
                    clean_key = key.strip()
                    clean_val = value.strip()
                    
                    # Auto-cast numeric strings to float/int, keep text as string
                    try:
                        if '.' in clean_val:
                            processed_row[clean_key] = float(clean_val)
                        else:
                            processed_row[clean_key] = int(clean_val)
                    except ValueError:
                        processed_row[clean_key] = clean_val
                        
                rules_list.append(processed_row)
                
        rules_schema = {
            "rules_metadata": {
                "source_file": input_csv,
                "total_parameters": len(rules_list)
            },
            "rules": rules_list
        }
            
        with open(output_json, mode='w', encoding='utf-8') as json_file:
            json.dump(rules_schema, json_file, indent=4)
            
        print(f"Successfully converted '{input_csv}' into '{output_json}' dynamically ({len(rules_list)} rules loaded)!")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "regulatory_rules.json"
        convert_csv_to_json(input_file, output_file)
    else:
        print("Usage: python convert_rules_dynamic.py <input_csv_file> [output_json_file]")

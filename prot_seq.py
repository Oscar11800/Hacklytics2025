import pandas as pd
from typing import Callable
import csv
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import functools
import requests

def get_protein_sequence(protein_id):
    url = f"https://www.ebi.ac.uk/proteins/api/proteins/{protein_id}"
    headers = {"Accept": "application/json"}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("sequence", {}).get("sequence", "No sequence found")
    else:
        return f"Error: {response.status_code}, {response.text}"

def process_single_value(value):
    """Helper function to process a single value"""
    try:
        result = get_protein_sequence(value)
        return {'value': value, 'result': result}
    except Exception as e:
        print(f"Error processing {value}: {str(e)}")
        return None

def main():
    df = pd.read_csv('HomoSapiens_binary_hq.txt', sep='\t')
    
    # Get unique values
    unique_values = df['Uniprot_A'].unique()
    
    # Set number of processes
    n_processes = 40
    
    # Process values in parallel
    with Pool(processes=n_processes) as pool:
        results = list(tqdm(
            pool.imap(process_single_value, unique_values),
            total=len(unique_values),
            desc="Processing proteins"
        ))
    
    # Filter out None values from errors
    results = [r for r in results if r is not None]
    
    # Save to CSV
    output_file = 'prot_seq.csv'
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['value', 'result'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Processed {len(results)} unique values and saved to {output_file}")

if __name__ == '__main__':
    main()

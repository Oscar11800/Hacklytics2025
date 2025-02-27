import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import requests

import matplotlib.pyplot as plt
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
import numpy as np
import os

from Bio.PDB import PDBList
import torch


import requests
import json
import random


def pdb_to_uniprot(pdb_id):

    d = {
        "4R7D" : "A0A0M3KKW6",
        "5GXQ" : "A0A1X8XL64",
        "7MRJ" : "A0A2R8Y7D0",
        "6SGE" : "A0A4E0W6L3",
        "6PYJ" : "A0A583ZBQ2"
    }
    return d[pdb_id]

    # url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
    # response = requests.get(url)
    #
    # if response.status_code == 200:
    #     data = response.json()
    #
    #     # Check for UniProt IDs in the 'struct_ref' section
    #     if 'struct_ref' in data:
    #         uniprot_ids = [ref['db_id'] for ref in data['struct_ref'] if ref['db_name'] == 'UNP']
    #         if uniprot_ids:
    #             return uniprot_ids
    #         else:
    #             return "No UniProt ID found in the PDB entry."
    #     else:
    #         return "No database references found in the PDB entry."
    # else:
    #     return f"Error: Unable to fetch data for PDB ID {pdb_id}"

# def pdb_to_uniprot(pdb_id):
#     url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         data = response.json()
#
#         # Extract UniProt IDs from the response
#         uniprot_ids = set()  # Use a set to avoid duplicates
#         if "rcsb_polymer_entity_container_identifiers" in data:
#             for entity in data["rcsb_polymer_entity_container_identifiers"]:
#                 if "reference_sequence_identifiers" in entity:
#                     for ref_seq in entity["reference_sequence_identifiers"]:
#                         if ref_seq["database_name"].upper() == "UNIPROT":
#                             uniprot_ids.add(ref_seq["database_accession"])
#
#         if not uniprot_ids:
#             raise Exception(f"No UniProt IDs found for PDB ID {pdb_id}.")
#
#         return list(uniprot_ids)
#
#     except requests.exceptions.RequestException as e:
#         raise Exception(f"Failed to fetch UniProt IDs for PDB ID {pdb_id}: {e}")

def uniprot_to_pdb(uniprot_id):
    url = "https://search.rcsb.org/rcsbsearch/v2/query"
    query = {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                        "operator": "exact_match",
                        "value": uniprot_id
                    }
                }
            ],
            "label": "text"
        },
        "return_type": "entry"
    }
    response = requests.post(url, json=query)
    if response.status_code == 200:
        data = response.json()
        pdb_ids = [result["identifier"] for result in data["result_set"]]
        return pdb_ids
    else:
        raise Exception(f"Failed to fetch PDB IDs for UniProt ID {uniprot_id}")


def fetch_pdb_file(pdb_id):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch PDB file for {pdb_id}")

def serve_pdb_file(request, pdb_id):
    pdb_content = fetch_pdb_file(pdb_id)  # Use the fetch_pdb_file function from earlier
    response = HttpResponse(pdb_content, content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="{pdb_id}.pdb"'
    return response


from django.shortcuts import render
from django.http import HttpResponseBadRequest

def get_pdb_info(pdb_id):
    if not pdb_id:
        return {"error": "Missing pdb_id parameter"}

    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"Failed to fetch data for PDB ID {pdb_id}"}

    data = response.json()

    pdb_info = {
        # Title of the PDB entry, describing the structure (e.g., protein, DNA, or complex)
        "Title": data.get("struct", {}).get("title", "N/A"),

        # DOI (Digital Object Identifier) for the PDB entry, if available
        "PDB DOI": data.get("rcsb_entry_container_identifiers", {}).get("doi", "N/A"),

        # Classification of the structure based on keywords (e.g., enzyme, signaling protein)
        "Classification": data.get("struct_keywords", {}).get("pdbx_keywords", "N/A"),

        # Organism(s) associated with the structure, listed as scientific names

        # Indicates whether mutations are present in the structure
        "Mutation(s)": "Yes" if data.get("pdbx_entry_details", {}).get("nonpolymer_details") else "No",

        # Date when the structure was initially deposited in the PDB
        "Deposited": data.get("pdbx_database_status", {}).get("recvd_initial_deposition_date", "N/A"),

        # Date when the structure was released to the public
        "Released": data.get("pdbx_database_status", {}).get("pdbx_database_release_date", "N/A"),

        # Additional fields for expanded metadata
        # Resolution of the structure (if available), indicating the quality of the model
        "Resolution (Å)": data.get("rcsb_entry_info", {}).get("resolution_combined", "N/A"),

        # Experimental method used to determine the structure (e.g., X-ray, NMR, Cryo-EM)
        "Experimental Method": data.get("rcsb_entry_info", {}).get("experimental_method", "N/A"),

        # Number of polymer entities (e.g., proteins, nucleic acids) in the structure
        "Polymer Entities": len(data.get("polymer_entities", [])),

        # Number of non-polymer entities (e.g., ligands, ions) in the structure
        "Non-Polymer Entities": len(data.get("nonpolymer_entities", [])),

    }

    return pdb_info

def view_pdb(request):
    if request.method == "GET":
        # Retrieve the 'identifier' from the URL query parameters
        input_tensor = torch.load(os.path.join(settings.BASE_DIR, "protein", "smallembed.pt"), map_location=torch.device('cpu'))
        print(input_tensor.keys())
        identifier = request.GET.get("identifier", "").strip().upper()
        print(1)
        # If no identifier is provided, render the template without a PDB ID
        if not identifier:
            return render(request, "base.html", {"identifier": None, "pdb_id": None})
            print(2)

        # Check if the identifier is a PDB ID (4-character alphanumeric)
        if len(identifier) == 4 and identifier.isalnum():
            pdb_id = identifier
            print(3)
        else:
            # Assume it's a UniProt ID and try to map it to PDB IDs
            try:
                pdb_ids = uniprot_to_pdb(identifier)
                if not pdb_ids:
                    return HttpResponseBadRequest(f"No PDB IDs found for UniProt ID {identifier}.")
                pdb_id = pdb_ids[0]  # Use the first PDB ID in the list
                print(4)
            except Exception as e:
                print(5)
                return HttpResponseBadRequest(str(e))


        pdb_info = get_pdb_info(pdb_id)
        uniprot_id = pdb_to_uniprot(pdb_id)
        top_id_uniprot = inference(uniprot_id)
        all_pdb_ids = []  # List to store all PDB IDs

        print(6)
        for uniprot_id in top_id_uniprot:
            try:
                # Call your existing uniprot_to_pdb function
                pdb_ids = uniprot_to_pdb(uniprot_id)
                all_pdb_ids.extend(pdb_ids)  # Add the PDB IDs to the flat list
            except Exception as e:
                # Handle errors (e.g., no PDB IDs found for a UniProt ID)
                print(f"Error converting UniProt ID {uniprot_id} to PDB IDs: {e}")

        # Render the template with the identifier and pdb_id

        return render(request, "base.html", {"pdb_info": pdb_info,"all_pdb_ids": all_pdb_ids, "identifier": identifier, "pdb_id": pdb_id})

def inference(uniprot_id):
    model = torch.jit.load(os.path.join(settings.BASE_DIR, "model_traced.pt"), map_location=torch.device('cpu'))
    print(uniprot_id)
    model.eval()
    input_tensor = torch.load("/Users/tejaakella/Desktop/Hacklytics2025/cogito/protein/smallembed.pt",
                              map_location=torch.device('cpu'))[uniprot_id]

    with torch.no_grad():
        output = model(input_tensor)

    top_values, top_indices = torch.topk(output, 10, largest=True)[:10]

    with open(os.path.join(settings.BASE_DIR, "ind_to_id.json")) as f:
        indices_to_ids = json.load(f)

    top_ids = [indices_to_ids[str(idx.item())] for idx in top_indices]
    print(top_ids)
    return top_ids

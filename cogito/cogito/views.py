import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import requests

import matplotlib.pyplot as plt
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
import numpy as np

from Bio.PDB import PDBList

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
        "title": data.get("struct", {}).get("title", "N/A"),
        "PDB DOI": data.get("rcsb_entry_container_identifiers", {}).get("doi", "N/A"),
        "Classification": data.get("struct_keywords", {}).get("pdbx_keywords", "N/A"),
        "Organism(s)": ", ".join([s.get("scientific_name", "N/A") for s in
                                  data.get("rcsb_entry_container_identifiers", {}).get("taxonomy", [])]),
        "Mutation(s)": "Yes" if data.get("pdbx_entry_details", {}).get("nonpolymer_details") else "No",
        "Deposited": data.get("pdbx_database_status", {}).get("recvd_initial_deposition_date", "N/A"),
        "Released": data.get("pdbx_database_status", {}).get("pdbx_database_release_date", "N/A"),
        "Deposition Author(s)": ", ".join(data.get("audit_author", []))
    }

    return pdb_info

def view_pdb(request):
    if request.method == "GET":
        # Retrieve the 'identifier' from the URL query parameters
        identifier = request.GET.get("identifier", "").strip().upper()

        # If no identifier is provided, render the template without a PDB ID
        if not identifier:
            return render(request, "protein/base.html", {"identifier": None, "pdb_id": None})

        # Check if the identifier is a PDB ID (4-character alphanumeric)
        if len(identifier) == 4 and identifier.isalnum():
            pdb_id = identifier
        else:
            # Assume it's a UniProt ID and try to map it to PDB IDs
            try:
                pdb_ids = uniprot_to_pdb(identifier)
                if not pdb_ids:
                    return HttpResponseBadRequest(f"No PDB IDs found for UniProt ID {identifier}.")
                pdb_id = pdb_ids[0]  # Use the first PDB ID in the list
            except Exception as e:
                return HttpResponseBadRequest(str(e))

        pdb_info = get_pdb_info(pdb_id)
        # Render the template with the identifier and pdb_id
        return render(request, "protein/base.html", {"identifier": identifier, "pdb_id": pdb_id, "pdb_info": pdb_info})




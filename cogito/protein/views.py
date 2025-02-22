import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import requests

import matplotlib.pyplot as plt
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
import numpy as np

from Bio.PDB import PDBList


def docking_graph(request):
    # Example docking scores (binding energies in kcal/mol)
    docking_scores = [-8.4, -7.2, -6.5, -9.1, -8.0]
    ligands = ['Ligand A', 'Ligand B', 'Ligand C', 'Ligand D', 'Ligand E']

    # Plotting the docking scores
    plt.figure(figsize=(8, 6))
    plt.bar(ligands, docking_scores, color='blue')
    plt.xlabel('Ligands')
    plt.ylabel('Binding Energy (kcal/mol)')
    plt.title('Docking Binding Energy')

    # Saving plot to an HTTP response (as PNG)
    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format="png")
    plt.close()  # Close the plot to free memory

    return response

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


def view_pdb(request):
    if request.method == "GET":
        identifier = request.GET.get("identifier", "").strip().upper()

        # If no identifier is provided, just render the template without a PDB ID
        if not identifier:
            return render(request, "protein/visual.html", {"pdb_id": None})

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

        return render(request, "protein/visual.html", {"pdb_id": pdb_id})
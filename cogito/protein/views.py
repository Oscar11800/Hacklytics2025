import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
from django.http import HttpResponse
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


def fetch_pdb(request, pdb_id):
    pdbl = PDBList()
    file_path = pdbl.retrieve_pdb_file(pdb_id, pdir="pdb_files", file_format="pdb")

    # Serve the PDB file as a response
    with open(file_path, "r") as file:
        response = HttpResponse(file.read(), content_type="chemical/x-pdb")
        response['Content-Disposition'] = f'attachment; filename="{pdb_id}.pdb"'
        return response

def visual(request):
    context = {
        "pdb_id": "1HHO"  # Example PDB ID, replace with real data
    }
    return render(request, "protein/visual.html", context)
    # return render(request, "protein/visual.html")
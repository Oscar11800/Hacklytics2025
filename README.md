# Protein AI
ProteinAI leverages ESM-2 and Alpha Fold PLMs and neural networks to accurately predict potential protein-protein interactions with uses in disease-related protein associations and drug development.
## Update: Winner of Hacklytics 2025! 
## Inspiration  
Our work was inspired by novel advancements in biocomputation, such as the Nobel Prize-winning AlphaFold and deep-learning research in protein binding prediction. We were interested in applying generative AI to tackle biological challenges.  

Some of our team members have recently taken courses on machine learning in biology and molecular dynamics simulations, and we were excited to apply our knowledge in a real-world project.  

A huge thank you to **GT and Hacklytics** for providing computing resources!  

---

## What It Does  
- Given a protein ID (UniProt or RCSB), ProteinAI runs a feed-forward neural network using embeddings from Meta’s ESM2 protein language model and AlphaFold to predict potential protein-protein interactions (PPIs).  
ProteinAI then generates side-by-side 3D visualizations of the target protein and a user-selected interacting protein.  
---

## How We Built It  

### **Data Preparation**  
- We used the HINT dataset to obtain a list of protein-protein interactions, and we preprocessed the dataset into a one-hot encoded format, where each protein is represented as a vector of its interactions.  
- Using UniProt IDs, we fetched the amino acid sequences of each protein via the UniProt API.  

### **Machine Learning Model**  
- Our main model is a feed-forward neural network trained on ESM2 sequence and Alpha Fold structural embeddings.  
- We treated the task as a downstream classification problem using PyTorch for training and testin on top of ESM2’s sequence embeddings.  
- We experimented with different hidden layer sizes and dimensions to optimize performance, trading off between precision and recall.

### **3D Visualization**  
- We realized that visualizing protein structures in 3D would make the data more useful beyond pure statistics since the structure of a protein had the strongest indication of its function.  
- We used NGL Viewer, a web-based molecular graphics tool that renders PDB coordinate structures.  

---

## Challenges We Ran Into  
  - One protein sequence (Titin) had 35k residues which exceeded CUDA memory limits, so we had to truncate sequences above 10k residues. We ended up removing 3 out of 16k proteins.  
  - Mapping STRING IDs to UniProt IDs was difficult and time consuming since gene -> protein mapping was not a one-to-one relationship.
  - Because many proteins do not interact,  we had a large class imbalance (99.9% negative labels), which led to achieving falsely high accuracy. Our solution was to implement a weighted loss function to penalize false negatives more than false positives.  
---

## Accomplishments We're Proud Of  
- Successfully integrating 3D visualization and making it work in real-time.  
- Implementing a  search function that integrates protein file generation while keeping a clean UI 
- Taking a dataset from raw data → neural network → functional PPI predictions  in such a short time!  

---

## What We Learned  
  - How deep learning is revolutionizing protein research.  
  - The complexities of protein-protein interactions beyond just sequence data(e.g., 3D structure matters).  
  - We learned practical lessons such as: Always save your work frequently, and get enough sleep!
---

## What's Next for ProteinAI  
- We plan to  store previously searched proteins in SQLite for faster retrieval and better 3D visualization performance.  
  - We would like to add customizable representation modes( e.g., space-filling, ribbon, surface models).  
- We would like to simulate multiple interacting proteins in the same environment.

if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")

BiocManager::install("biomaRt")
library(biomaRt)

# Load necessary libraries
library(biomaRt)
library(dplyr)
library(readr)

# Read the data (space-separated values)
df <- read.delim("protein_links.txt", sep = "", header = TRUE, stringsAsFactors = FALSE)

# Use biomaRt to get UniProt IDs
ensembl <- useMart("ensembl", dataset = "hsapiens_gene_ensembl")

# Convert first 5 STRING IDs to UniProt
string_ids <- unique(c(df$protein1[1:5], df$protein2[1:5]))

conversion_table <- getBM(
  attributes = c("ensembl_peptide_id", "uniprotswissprot"),
  filters = "ensembl_peptide_id",
  values = string_ids,
  mart = ensembl
)

# Create a mapping table
string_to_uniprot <- setNames(conversion_table$uniprotswissprot, conversion_table$ensembl_peptide_id)

# Replace STRING IDs with UniProt IDs in the first 5 rows
df[1:5, "protein1"] <- ifelse(df[1:5, "protein1"] %in% names(string_to_uniprot),
                              string_to_uniprot[df[1:5, "protein1"]],
                              df[1:5, "protein1"])

df[1:5, "protein2"] <- ifelse(df[1:5, "protein2"] %in% names(string_to_uniprot),
                              string_to_uniprot[df[1:5, "protein2"]],
                              df[1:5, "protein2"])

# Save the updated file
output_file <- file.path(script_dir, "converted_protein_ids.txt")
write.table(df[1:5, ], file = output_file, sep = "\t", row.names = FALSE, quote = FALSE)

cat("Conversion complete. First 5 rows saved at:", output_file, "\n")

import sys
import re
import argparse
from Bio import SeqIO
from Bio.SeqUtils import ProtParam
from collections import Counter

def aliphatic_index(sequence):
    aliphatic_aa = {'A': 0.283, 'V': 0.606, 'I': 0.530, 'L': 0.603}
    return sum(aliphatic_aa.get(aa, 0) for aa in sequence) / len(sequence) * 100

def protein_formula(sequence):
    amino_acid_formulas = {
        'A': 'C3H5NO',
        'C': 'C3H5NOS',
        'D': 'C4H5NO3',
        'E': 'C5H7NO3',
        'F': 'C9H9NO',
        'G': 'C2H3NO',
        'H': 'C6H7N3O',
        'I': 'C6H11NO',
        'K': 'C6H12N2O',
        'L': 'C6H11NO',
        'M': 'C5H9NOS',
        'N': 'C4H6N2O2',
        'P': 'C5H7NO',
        'Q': 'C5H8N2O2',
        'R': 'C6H12N4O',
        'S': 'C3H5NO2',
        'T': 'C4H7NO2',
        'V': 'C5H9NO',
        'W': 'C11H10N2O',
        'Y': 'C9H9N1O2'
    }
    
    formula_counter = Counter()
    element_pattern = re.compile("([A-Z][a-z]*)(\d*)")

    for aa in sequence:
        formula = amino_acid_formulas[aa]
        elements_counter = Counter({match.group(1): int(match.group(2) or '1') for match in element_pattern.finditer(formula)})
        formula_counter += elements_counter

    # Subtract one water molecule for each peptide bond
    formula_counter['H'] -= (len(sequence) - 1)
    formula_counter['O'] -= (len(sequence) - 1)

    return ''.join([f"{element}{count}" for element, count in formula_counter.items()])


def analyze_proteins(fasta_file, output_file):
    with open(fasta_file, "r") as f:
        records = []
        current_id = ""
        current_seq = []
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_id and current_seq and "pep" in current_id:
                    records.append((current_id, "".join(current_seq)))
                current_id = line[1:]
                current_seq = []
            elif line and not line.startswith("--"):
                current_seq.append(line)
        # Add the last record
        if current_id and current_seq and "pep" in current_id:
            records.append((current_id, "".join(current_seq)))

    with open(output_file, "w") as out_f:
        header = "ID,Protein Length,CDS Length,Protein Molecular Weight (kDa),Protein Isoelectric Point,Protein Hydrophilicity,Protein Aliphatic Index,Protein Instability Index,Protein Formula\n"
        out_f.write(header)

        for record_id, sequence in records:
            protein_length = len(sequence)
            cds_length = protein_length * 3
            protein_analyzer = ProtParam.ProteinAnalysis(sequence)
            molecular_weight = protein_analyzer.molecular_weight() / 1000
            isoelectric_point = protein_analyzer.isoelectric_point()
            hydrophilicity = protein_analyzer.gravy()
            aliphatic_idx = aliphatic_index(sequence)
            instability_index = protein_analyzer.instability_index()
            formula = protein_formula(sequence)

            line = f"{record_id.split()[0]},{protein_length},{cds_length},{molecular_weight:.4f},{isoelectric_point:.4f},{hydrophilicity:.4f},{aliphatic_idx:.4f},{instability_index:.4f},{formula}\n"
            out_f.write(line)

def main():
    parser = argparse.ArgumentParser(description="Analyze protein sequences in a FASTA file and save the results in a CSV file.")
    parser.add_argument("--fasta", required=True, help="Input FASTA file containing protein sequences.")
    parser.add_argument("--csv", required=True, help="Output CSV file to store the results.")

    args = parser.parse_args()
    analyze_proteins(args.fasta, args.csv)

if __name__ == "__main__":
    main()

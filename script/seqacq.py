import sys

def parse_fasta(file_path):
    sequences = {}
    with open(file_path, 'r') as file:
        sequence_id = ''
        sequence = ''
        for line in file:
            line = line.strip()
            if line.startswith('>'):
                if sequence_id:
                    sequences[sequence_id] = sequence

                sequence_id = line[1:].split()[0]  # Remove '>' from the header
                sequence = ''
            else:
                sequence += line
        if sequence_id:
            sequences[sequence_id] = sequence
    return sequences

def extract_sequence(sequences, seq_id, start, end):
    if seq_id in sequences:
        sequence = sequences[seq_id]
        if start < 1 or end > len(sequence):
            raise ValueError("Start or end position is out of range.")
        return sequence[start-1:end]  # Python uses 0-based indexing
    else:
        raise ValueError(f"Sequence ID '{seq_id}' not found in the FASTA file.")

def main():
    if len(sys.argv) != 5:
        print("Usage: python extract_sequence.py <fasta_file> <sequence_id> <start> <end>")
        sys.exit(1)

    fasta_file = sys.argv[1]
    seq_id = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])

    sequences = parse_fasta(fasta_file)
    try:
        extracted_sequence = extract_sequence(sequences, seq_id, start, end)
        print(f">{seq_id}_{start}_{end}")
        print(extracted_sequence)
    except ValueError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()

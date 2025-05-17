# For each variant in the vcf, check reference allele matches FASTA

import vcfpy
import argparse
from pyfaidx import Fasta # indexed acess, faster than biopython

def check_ref(f: str, fasta_file):
    reader = vcfpy.Reader.from_path(f)
    fasta = Fasta(fasta_file) # Create an index the first time

    for record in reader:
        ref = fasta[record.CHROM][record.POS]
        if record.REF != ref:
            print(f"Mismatch at {record.CHROM}:{record.POS}: got {record.REF}, expected {ref}")
            print(f"AF={record.INFO['AF']}")


def main():
    parser = argparse.ArgumentParser(
        description='Check reference allele vs FASTA'
    )
    parser.add_argument('input_file', help='Input text file')
    parser.add_argument('fasta', help='FASTA')

    args = parser.parse_args()

    check_ref(args.input_file, args.fasta)

    
if __name__ == '__main__':
    main()


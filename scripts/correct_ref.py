# For each variant, correct REF so that it matches FASTA.
# Used for variants in paralog regions

import vcfpy
import argparse
from pyfaidx import Fasta # indexed acess, faster than biopython

def check_ref(f_in: str, f_out: str, fasta_file: str):
    reader = vcfpy.Reader.from_path(f_in)
    writer = vcfpy.Writer.from_path(f_out, reader.header)
    fasta = Fasta(fasta_file) # Create an index the first time

    for record in reader:
        ref = fasta[record.CHROM][record.POS]
        if record.REF != ref:
            record.REF = ref
        writer.write_record(record)



def main():
    parser = argparse.ArgumentParser(
        description='Check reference allele vs FASTA'
    )
    parser.add_argument('input_file', help='Input text file')
    parser.add_argument('output_file', help='Output text file')
    parser.add_argument('-f', '--fasta', help='FASTA')

    args = parser.parse_args()

    check_ref(args.input_file, args.output_file, args.fasta)

    
if __name__ == '__main__':
    main()


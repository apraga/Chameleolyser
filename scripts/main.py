#!/usr/bin/env python3
"""
Convert pseudogene variant text format to VCF using vcfpy.
Each input line contains two candidate variants where only one is true.
"""

import sys
import vcfpy # no vcf in biopython
import re
import argparse
import subprocess
from pyfaidx import Fasta # indexed acess, faster than biopython

def parse_variant(variant_str: str, info, dp: float, fasta) -> vcfpy.Record:
    """Parse a variant string in the format chr~pos~end~ref/alt."""
    parts = variant_str.split('~')
    chrom = parts[0]
    pos = int(parts[1])

    # Handle the ref/alt part
    ref_alt = parts[3].split('/')


    if ref_alt[1] == '-':
        # Deletion

        pos = pos - 1
        prev = fasta[chrom][pos-1]
        ref = str(prev) + ref_alt[0]
        alt = prev
     

        alt_objs = [vcfpy.Substitution("DEL", str(alt))]
        # Insertion
    elif ref_alt[0] == '-':
        pos = pos - 1
        prev = fasta[chrom][pos]
        ref = prev
        alt = str(prev) + ref_alt[1]

        alt_objs = [vcfpy.Substitution("INS", alt)]
    else:
        ref = ref_alt[0]
        alt = ref_alt[1]
        alt_objs = [vcfpy.Substitution("SNV", alt)]




    vaf = float(info['AF'])
    sample = {'GT': genotype(vaf, alt), 'DP': dp}


    return vcfpy.Record(
        CHROM=chrom,
        POS=pos,
        ID=[],
        REF=ref,
        ALT=alt_objs,
        QUAL=None,
        FILTER=['PASS'],
        INFO=info,
        FORMAT=['GT', 'DP'],
        calls=[vcfpy.Call('Chameleolyzer', data=sample)]
    )

def get_fields(line):
    """ None if splitting the line failed"""
    line = line.strip()
    if not line:
        return None

    fields = line.split()
    if len(fields) < 6:
        sys.stderr.write(f"Skipping malformed line: {line}\n")
        return None

    if fields[0] == "Chromosome":
        print("Skipping header")
        return None
    return fields

def genotype(vaf: float, alt: str) -> str:
    if alt == "-":
        return "0/0"
    elif vaf > 0.8:
        return "1/1"
    else:
        return "0/1"

def candidate_records(line: str, fasta):
    """ List of candidate from text file
    Format :
    Chromosome	Star
            print(f"  Writing record: {records[0]}")t	VAP	VariantCall	VAF_Masked	MaskedCov	PopFreq
    with Variant=chr10~100348079~100348078~-/ACC
    """
    fields = get_fields(line)
    if fields is None:
        return []

    info = {
        'AF': fields[4],
        # Keep track those variants are 2 candidates for the same variant
        'Pseudogene': f"{fields[0]}-{fields[1]}"
    }

    # Parse both variants
    var1 = parse_variant(fields[2], info, fields[5], fasta)
    var2 = parse_variant(fields[3], info, fields[5], fasta)

    records = [var1 ]
    # Don't compare records as it recurses infinitively
    if fields[2] != fields[3]:
        records += [ var2 ]
    return records

def convert_to_vcf(input_file, output_file, fasta_file):
    """Convert the input format to VCF format."""
    fasta = Fasta(fasta_file) # Create an index the first time
    # Read header from file
    header = vcfpy.Reader.from_path('template.vcf').header
    # Adding sample is important for hap.py
    header.samples = vcfpy.SamplesInfos(["Chameleolyzer"])
    with vcfpy.Writer.from_path(output_file, header) as writer:
        with open(input_file, 'r') as f:
            for line in f:
                records = candidate_records(line, fasta)
                if not records :
                    continue
                writer.write_record(records[0])

    print(f"Wrote {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Convert pseudogene variant text format to VCF using vcfpy'
    )
    parser.add_argument('input_file', help='Input text file')
    parser.add_argument('output_file', help='Output VCF file')
    parser.add_argument('fasta', help='FASTA')

    args = parser.parse_args()

    convert_to_vcf(args.input_file, "tmp.vcf", args.fasta)
    print("Sorting file")
    subprocess.run(["bcftools", "sort", "tmp.vcf", "-o", args.output_file])
    print("Checking output...")
    subprocess.run(["vcfcheck", args.output_file, "-f", args.fasta])
    #
if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Convert pseudogene variant text format to VCF using vcfpy.
Each input line contains two candidate variants where only one is true.
"""

import sys
import vcfpy
import re
import argparse


def parse_variant(variant_str: str, info, dp: float) -> vcfpy.Record:
    """Parse a variant string in the format chr~pos~end~ref/alt."""
    parts = variant_str.split('~')
    chrom = parts[0]
    pos = int(parts[1])
    
    # Handle the ref/alt part
    ref_alt = parts[3].split('/')
    # If ref is empty, use N as placeholder (VCF requires a reference base)
    ref = 'N' if ref_alt[0] == '-' else ref_alt[0]
    alt = ref_alt[1]

    vaf = float(info['AF'])
    sample = {'GT': genotype(vaf), 'DP': dp}

    # For substitutions and insertions
    alt_objs = [vcfpy.Substitution("SNV", alt)]
    if alt == '-':
        alt_objs = [vcfpy.Substitution("DEL", [])]
    if ref == 'N':
        alt_objs = [vcfpy.Substitution("INS", alt)]

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

def genotype(vaf: float) -> str:
    return "1/1" if vaf > 0.8 else "0/1"
        
def candidate_records(line: str):
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
    var1 = parse_variant(fields[2], info, fields[5])
    var2 = parse_variant(fields[3], info, fields[5])

    records = [var1 ]
    # Don't compare records as it recurses infinitively
    if fields[2] != fields[3]: 
        records += [ var2 ]
    return records

def convert_to_vcf(input_file, output_file):
    """Convert the input format to VCF format."""
    # Read header from file
    header = vcfpy.Reader.from_path('template.vcf').header
    # Adding sample is important for hap.py
    header.samples = vcfpy.SamplesInfos(["Chameleolyzer"])
    with vcfpy.Writer.from_path(output_file, header) as writer:
        with open(input_file, 'r') as f:
            for line in f:
                records = candidate_records(line)
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
    
    args = parser.parse_args()
    convert_to_vcf(args.input_file, args.output_file)

if __name__ == '__main__':
    main()

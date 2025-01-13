#!/usr/bin/env python3
"""
Convert pseudogene variant text format to VCF using vcfpy.
Each input line contains two candidate variants where only one is true.
"""

import sys
import vcfpy
import re
import argparse

def parse_variant(variant_str):
    """Parse a variant string in the format chr~pos~end~ref/alt."""
    parts = variant_str.split('~')
    chrom = parts[0]
    pos = int(parts[1])
    
    # Handle the ref/alt part
    ref_alt = parts[3].split('/')
    ref = '' if ref_alt[0] == '-' else ref_alt[0]
    alt = '' if ref_alt[1] == '-' else ref_alt[1]
    
    return {'chrom': chrom, 'pos': pos, 'ref': ref, 'alt': alt}

def get_fields(line):
    """ None if splitting the line failed"""
    line = line.strip()
    if not line:
        return None

    fields = line.split()
    if len(fields) < 6:
        sys.stderr.write(f"Line {line_num}: Skipping malformed line: {line}\n")
        return None

    if fields[0] == "Chromosome":
        print("Skipping header")
        return None
    return fields

def candidate_records(line):
    """ List of candidate from text file
    Format : """
    fields = get_fields(line)
    if fields is None:
        return []

    # Parse both variants
    var1 = parse_variant(fields[2])
    var2 = parse_variant(fields[3])

    # Check if variants are identical
    records = [var1 ]
    if var1 != var2:
        records += [ var2 ]
    return records

def convert_to_vcf(input_file, output_file):
    """Convert the input format to VCF format."""
    # Read header from file
    # Open input, add FILTER header, and open output file
    reader = vcfpy.Reader.from_path('template.vcf')
    reader.header.add_filter_line(vcfpy.OrderedDict([
        ('ID', 'DP10'), ('Description', 'total DP < 10')]))
    
    # Initialize VCF writer
    writer = vcfpy.Writer.from_path(output_file, reader.header)
    
    # Process input file
    with open(input_file, 'r') as f:
        for line in f:
            records = candidate_records(line)
            
            # alt_depth = int(fields[6]) if len(fields) > 6 else 0
            # # For the VCF record, use the first variant as primary
            # # If REF is empty, use N as placeholder (VCF requires a reference base)
            # ref = var1['ref'] if var1['ref'] else 'N'
            # 
            # # Handle ALT field
            # if var1['alt']:
            #     alt = [vcfpy.Substitution(var1['alt'])]
            # else:
            #     # For deletions, use <DEL> symbolic allele
            #     alt = [vcfpy.SymbolicAllele('<DEL>')]
            # 
            # # Create INFO dictionary
            # info = {
            #     'AF': allele_freq,
            #     'DP': read_depth,
            #     'AltDP': alt_depth
            # }
            # 
            # # Add the second variant as an INFO field if they're different
            # if not are_identical:
            #     var2_info = f"{var2['chrom']}:{var2['pos']}:{var2['ref'] or '-'}:{var2['alt'] or '-'}"
            #     info['PseudogeneCandidate'] = var2_info
            # 
            # # Create a VCF record
            # record = vcfpy.Record(
            #     CHROM=chrom,
            #     POS=position,
            #     ID=[],
            #     REF=ref,
            #     ALT=alt,
            #     QUAL=None,
            #     FILTER=['PASS'],
            #     INFO=info,
            #     FORMAT=['GT'],
            #     calls=[vcfpy.Call('SAMPLE', {'GT': vcfpy.GenotypeType('0/1')})]
            # )
            # 
            # # Write the record
            # writer.write_record(record)
    
    writer.close()

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

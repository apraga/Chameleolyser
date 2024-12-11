#!/bin/sh
# Convert chromosome from refseq to chr
url="https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_assembly_report.txt"
curl $url > assembly_report.txt
# Prepare sed commnands: skip comment and "na".
# Use fix and patch too
awk -F "\t" '
/^[^#]/ && $7 != "na" {
print "s/>"$7"/>"$10"/";
}' assembly_report.txt | tr -d $'\r' > mapping_from_refseq.sed
sed -i -f mapping_from_refseq.sed GCF_000001405.40_GRCh38.p14_genomic.fna

# Overview
Chameleolyser is a bioinformatics tool to identify genetic variants in homologous regions using whole-exome sequencing (WES) data. These variants remain hidden in a regular WES analysis. The current implementation of our software is hg19-based and is tested on CentOS Linux 7. However, it should run on any Linux OS. The only required input is a CRAM or BAM file.

# Installation
It is highly recommended to install all dependencies by cloning the Chameleolyser repository onto your machine. This procedure takes around 5 minutes.
```
git clone https://github.com/Genome-Bioinformatics-RadboudUMC/Chameleolyser.git
cd Chameleolyser/
conda env create -f ChameleolyserEnvironment.yml
conda activate Chameleolyser
```

# Usage
## Mask reference genome


Download reference genome, extract it:
```

wget
https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.26_GRCh38/GRCh38_major_release_seqs_for_alignment_pipelines/GCA_000001405.15_GRCh38_full_analysis_set.fna.gz
gunzip GCA_000001405.15_GRCh38_full_analysis_set.fna.gz

 wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.26_GRCh38/GRCh38_major_release_seqs_for_alignment_pipelines/GCA_000001405.15_GRCh38_full_analysis_set.fna.fai
```

The MaskReferenceGenome function will create a masked version of it. This option only need to be run once (also in case multiple samples are analysed in the same working directory). This step might take up to 90 minutes but only needs to be run once in case you wish to analyse multiple samples.
```
perl Chameleolyser.pl --MaskReferenceGenome --WORKING_DIR=work/
```

## Generate masked alignments and raw VCF
This function will extract reads in the homologous regions and re-align them to the masked reference sequence. Subsequently it will call variants with a sensitive method. The sample name is an identifier of choice. The alignment filepath is the full path of the CRAM/BAM file of your sample of interest which is stored on your machine.
Here is an example

```

perl Chameleolyser.pl --GenerateMaskedAlignmentAndVcf --WORKING_DIR=/Work/Users/apraga/Chameleolyser/work/  --SAMPLE_NAME=HG002-retest --ALIGNMENT_FP=/Work/Users/apraga/Chameleolyser/151002_7001448_0359_AC7F6GANXX_Sample_HG002-EEogPU_v02-KIT-Av5_AGATGTAC_L008.posiSrt.markDup_GRCh38_tagged.bam
```
## Filter raw variants

```
perl Chameleolyser.pl --WORKING_DIR=/Work/Users/apraga/Chameleolyser/work  --FilterRawVariants --SAMPLE_NAME=HG002-retest
```

This will result in variant in text format where each variant can also be on an alternate positions, for example ` work/RAW/HG002-retest-save/HG002-retest.Filter2SNVs.txt`

# Demo
## Download public exome sample
Download the BAM file (and the associated index) of HG002 into a directory of choice on your system.

```
wget ftp://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio/HG002_NA24385_son/OsloUniversityHospital_Exome/151002_7001448_0359_AC7F6GANXX_Sample_HG002-EEogPU_v02-KIT-Av5_AGATGTAC_L008.posiSrt.markDup.bam
wget ftp://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio/HG002_NA24385_son/OsloUniversityHospital_Exome/151002_7001448_0359_AC7F6GANXX_Sample_HG002-EEogPU_v02-KIT-Av5_AGATGTAC_L008.posiSrt.markDup.bai
```

## Prepare BED
Since the 1000 genomes reference sequence is used to align the HG002 reads (thus no 'chr' prefix in the chromosome names), we run the following command. The working directory needs to be the full path of an existing directory on your system.

```
perl Chameleolyser.pl --PrepareBED --WORKING_DIR=<WORKING_DIRECTORY> --OMIM=yes
```

## Mask reference genome

```
perl Chameleolyser.pl --MaskReferenceGenome --WORKING_DIR=<WORKING_DIRECTORY> --OMIM=yes
```

## Generate masked alignments and raw VCF
ALIGNMENT_FP: Pass the complete path of the HG002 bam file that was downloaded in the first step in this demo.
```
perl Chameleolyser.pl --GenerateMaskedAlignmentAndVcf --WORKING_DIR=<WORKING_DIRECTORY> --OMIM=yes --SAMPLE_NAME=HG002 --ALIGNMENT_FP=<ALIGNMENT_FP> --NR_OF_THREADS=4
```

## Filter raw variants

```
perl Chameleolyser.pl --FilterRawVariants --WORKING_DIR=<WORKING_DIRECTORY> --SAMPLE_NAME=HG002
```

The filtered variant lists that should result from this operation can be found in the "DEMO_OUTPUT" folder in the repository.

# License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

Copyright (c) 2023 Wouter Steyaert

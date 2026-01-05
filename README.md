# Homer Peak Annotation
This script takes in a ONE-seq nomination file, converts it to a BED file, and then outputs the peak annotation for the inputted data


## Overview 
ONE-seq site nomination data should include:
- Chromosome 
- Location
- Identifier code
- Direction
- additional data

 We will use this information to create a BED file for use as the annotation input. The result will be all of the information homer annotation returns. This includes:
- Distance to nearest TSS
- Gene name
- Annotation
- Nearest refseq
- additional information

The full list of data returned can be found here: 
http://homer.ucsd.edu/homer/ngs/annotation.html

## Prerequisites
Assuming you're working with Conda, here is a set up guide for a use with this function

### 1. Conda Environment Setup
Create a new environment using 
```bash
conda create --name [yourChosenName] python=3.13
```

Activate the newly created environment using:
```bash
conda activate [yourChosenName]
```
We'll create a new conda environment for this project so we can continue to keep our different pipelines compartmentalized.

### 2. Python Packages 
using the Conda install command to install pandas 
```bash
conda install pandas
```

### 3. HOMER
We need to make a directory for all our HOMER information. Here's the order:
 ```bash
mkdir ~/homer
cd ~/homer
```

Then we need to download and install HOMER:
```bash
wget http://homer.ucsd.edu/homer/configureHomer.pl
perl configureHomer.pl -install
```

Now we're going to add HOMER to your PATH:
```bash
echo 'export PATH=$PATH:~/homer/bin/' >> ~/.bashrc
source ~/.bashrc
```
Double check that HOMER is accessible:
```bash
which annotatePeaks.pl
```

### 4. Install the genome
We now need to install the hg38 version of the human genome using this command:
```bash
perl ~/homer/configureHomer.pl -install hg38
```
It is worth noting that this could take sometime as it is several gigabytes.
We can check that hg38 installed correctly by using this command:
```bash
perl ~/homer/configureHomer.pl -list
```
`hg38` should be listed in the installed packages.

## Usage
### Input file format
The input file is a **tab separated text file** (TSV) that contains columns with the headers:
| Column Name  | Description                              | Example       |
|--------------|------------------------------------------|---------------|
| chromosome   | Chromosome name                          | chr1  |
| location     | Genomic position (1-based coordinate)    | 5259321       |
| direction    | Strand                                   | + or -        |
| frag_numb    | Unique identifier for each site          | ASD00039      |

It is of note that other information can exist within this file, but these columns are required.

### Running the Annotation
In an input folder beside the script you can place your input file. The naming convention can be whatever you'd like so long as its a Tab Separated Text File and is the only file within the input folder. After you have your input file in the correct place you can run the script using this command:
```bash
python annotate_peaks.py
```

A high level understanding of the operations performed by the script is listed below:

1) Script finds the input file in your `input/` folder
2) Script converts the input file into a BED file for HOMER
3) Homer peak annotation is performed
4) output file is created and placed in the `output/` folder

### Project Structure
```
YourWorkingDirectory/
├── annotate_peaks.py          # Main annotation script
├── input/                      # Place your input file here
│   └── your_data.txt          # Your input file (only one .txt file)
└── output/                     # Annotated results appear here
    └── your_data_annotated.txt # Output file (created by script)
```

## Output
The final output file (`your_data_annotated.txt`) is a **tab-separated text file** that combines your original input data with HOMER annotation results. The output contains the following columns:

| Column Name           | Description                                           |
|-----------------------|-------------------------------------------------------|
| chromosome            | Chromosome name (from input)                          |
| location              | Genomic position (from input)                         |
| direction             | Strand (from input)                                   |
| frag_numb             | Unique identifier (from input)                        |
| Annotation            | Primary genomic feature annotation                    |
| Detailed Annotation   | Extended annotation details                           |
| Distance to TSS       | Distance to nearest transcription start site (bp)     |
| Nearest PromoterID    | ID of the nearest promoter                            |
| Entrez ID             | NCBI Entrez Gene ID                                   |
| Nearest Unigene       | Nearest UniGene cluster ID                            |
| Nearest Refseq        | Nearest RefSeq transcript ID                          |
| Nearest Ensembl       | Nearest Ensembl gene ID                               |
| Gene Name             | Official gene symbol                                  |
| Gene Alias            | Alternative gene names                                |
| Gene Description      | Full gene description                                 |
| Gene Type             | Type of gene (e.g., protein-coding, lncRNA)           |

**Note:** Any additional columns from your input file will also be preserved in the output.

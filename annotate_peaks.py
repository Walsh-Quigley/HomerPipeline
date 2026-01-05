import pandas as pd
import subprocess
import sys
import os

def annotate_with_homer(input_file, genome="hg38"):
    ###find nearest gene and current genomic feature.
    
    #error handlign needed for if thers no input file from user

    #error handling needed if the annotation reference is missing

    bed_file = "temp_peaks.bed"
    homer_output = "temp_homer_annotation.txt"

    # Extract just the filename without path for output
    input_filename = os.path.basename(input_file)
    base_name = input_filename.replace('.txt', '')
    output_file = f"output/{base_name}_annotated.txt"


    print("Reading input file...")
    df = pd.read_csv(input_file, sep='\t')
    print(f"    Loaded {len(df)} rows")
    print(f"    Columns: {list(df.columns)}")

    print("\nConverting to BED format for HOMER...")
    bed_data = []
    for idx, row in df.iterrows():
        chrom = row['chromosome']
        pos = int(row['location'])
        strand = row['direction']
        name = row['frag_numb']

        #BED is 0 based, location is 1 based, thats why we do this
        start = pos - 1
        end = pos
        bed_data.append([chrom, start, end, name, 0, strand])


    bed_df = pd.DataFrame(bed_data, columns=['chr', 'start', 'end', 'name', 'score', 'strand'])
    bed_df.to_csv(bed_file, sep='\t', header=False, index=False)
    print(f"    Created BED file: {bed_file} with {len(bed_df)} regions")


    print("\nRunning Homer annotation...")
    cmd = [
        'annotatePeaks.pl', #peak annotation script
        bed_file, #Input BED file with peak positions
        genome, #gene annotation file
        '-cpu', '4' #number of CPU cores to use
    ]

    print(f"    Command: {' '.join(cmd)}")
    with open(homer_output, 'w') as outf:
        result = subprocess.run(cmd, stdout=outf, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"    Error: HOMER failed")
    
    print(" Homer annotation Complete!")


    print("\nParsing Homer output...")
    homer_df = pd.read_csv(homer_output, sep='\t')
    print(f"    Homer returned {len(homer_df)} annotations")
    print(f"    Available columns: {list(homer_df.columns)}")

    if 'Gene Name' in homer_df.columns:
        nearest_gene = homer_df['Gene Name']
    elif 'Nearest PromoterID' in homer_df.columns:
        nearest_gene = homer_df['Nearest PromoterID']
    #else:
        #this will be used if hte other two dont work

    if 'Annotation' in homer_df.columns:
        genomic_feature = homer_df['Annotation']
    elif 'Detailed Annotation' in homer_df.columns:
        genomic_feature = homer_df['Detailed Annotation']
    #else:
        #once again this is for if the other two dont work


    #cant depend on this, merges back in the wrong order
    #print("\nAdding annotations to original file...")
    #df['Nearest_Gene'] = nearest_gene.values
    #df['Genomic_Feature'] = genomic_feature.values

    #the fix
    # Extract all relevant HOMER columns
    homer_simple = pd.DataFrame({
        'frag_numb': homer_df[homer_df.columns[0]],  # First column is always PeakID
        'Annotation': homer_df['Annotation'],
        'Detailed Annotation': homer_df['Detailed Annotation'],
        'Distance to TSS': homer_df['Distance to TSS'],
        'Nearest PromoterID': homer_df['Nearest PromoterID'],
        'Entrez ID': homer_df['Entrez ID'],
        'Nearest Unigene': homer_df['Nearest Unigene'],
        'Nearest Refseq': homer_df['Nearest Refseq'],
        'Nearest Ensembl': homer_df['Nearest Ensembl'],
        'Gene Name': homer_df['Gene Name'],
        'Gene Alias': homer_df['Gene Alias'],
        'Gene Description': homer_df['Gene Description'],
        'Gene Type': homer_df['Gene Type']
    })

    df = df.merge(homer_simple, on='frag_numb', how='left')

    df.to_csv(output_file, sep='\t', index=False)
    print(f"    Saved annotated file: {output_file}")

    print("\nCleaning up temp files...")
    #os.remove(bed_file) 
    #os.remove(homer_output) #keeping this for now to see intermediate files

    print("\n" + "="*60)
    print("ANNOTATION COMPLETE!")
    print("="*60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Rows:   {len(df)}")
    print("\nFirst 5 examples:")
    print(df[['frag_numb', 'chromosome', 'location', 'Gene Name', 'Annotation']].head().to_string())
    return output_file

if __name__ == "__main__":
    import glob

    # Look for files in the input folder
    input_files = glob.glob("input/*.txt")

    if len(input_files) == 0:
        print("ERROR: No .txt files found in 'input/' folder")
        print("Please place your input file in the 'input/' directory")
        sys.exit(1)

    if len(input_files) > 1:
        print(f"ERROR: Found {len(input_files)} files in input/ folder:")
        for f in input_files:
            print(f"  - {f}")
        print("\nPlease ensure there is only ONE .txt file in the input/ folder")
        sys.exit(1)

    # Process the single file found
    annotate_with_homer(input_files[0])
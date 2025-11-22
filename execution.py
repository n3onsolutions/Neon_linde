from dotenv import load_dotenv
import os
from utils import process_pdf

def main():
    load_dotenv()
    input_pdf = os.getenv("INPUT_PDF", "EN_ds_c_matic_8925_en_e_1025_view.pdf")
    
    print(f"Processing {input_pdf}...")
    # process_pdf handles temp directories for images and doesn't save MD/Analysis unless requested (which we aren't)
    result = process_pdf(input_pdf)
    
    print("\n--- Analysis Result ---\n")
    print(result)

if __name__ == "__main__":
    main()


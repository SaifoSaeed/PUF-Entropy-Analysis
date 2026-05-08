import os
from pathlib import Path

def xor_files(file_a_path, file_b_path, output_path):
    """Reads two binary files, XORs them byte-by-byte, and writes the result."""
    try:
        with open(file_a_path, 'rb') as fa, open(file_b_path, 'rb') as fb:
            bytes_a = fa.read()
            bytes_b = fb.read()

        min_len = min(len(bytes_a), len(bytes_b))
        
        xor_result = bytes(a ^ b for a, b in zip(bytes_a[:min_len], bytes_b[:min_len]))

        with open(output_path, 'wb') as f_out:
            f_out.write(xor_result)
            
        print(f"[+] Generated: {output_path.name} (n={min_len * 8} bits)")
        
    except Exception as e:
        print(f"[-] Error processing {output_path.name}: {e}")

def main():
    dataset_dir = Path(r"C:\Users\jmorp\OneDrive\Desktop\Projects\HS-Assign3\proc_datasets")
    xor_dir = Path(r"C:\Users\jmorp\OneDrive\Desktop\Projects\HS-Assign3\xor_datasets")
    
    if not dataset_dir.exists():
        print("Dataset directory not found.")
        return

    voltages = ["477mV", "530mV", "540mV", "583mV", "600mV", "660mV", "720mV", "800mV", "880mV"]
    
    for voltage in voltages:
        v_dir = dataset_dir / voltage
        out_v_dir = xor_dir / voltage
        out_v_dir.mkdir(parents=True, exist_ok=True)
        
        chip1_path = v_dir / "chip1.bin"
        chip2_path = v_dir / "chip2.bin"
        chip3_path = v_dir / "chip3.bin"
        
        if chip1_path.exists() and chip2_path.exists():
            out_name = out_v_dir / "chip1_XOR_chip2.bin"
            xor_files(chip1_path, chip2_path, out_name)
            
        if chip2_path.exists() and chip3_path.exists():
            out_name = out_v_dir / "chip2_XOR_chip3.bin"
            xor_files(chip2_path, chip3_path, out_name)

if __name__ == "__main__":
    print("Generating XOR datasets for NIST STS evaluation...")
    main()
from pathlib import Path

def prepare_nist_dataset(src_dir="datasets", dest_dir="proc_datasets"):
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)

    if not src_path.exists():
        print(f"Error: Source directory '{src_path}' not found.")
        return

    for txt_file in src_path.rglob('*.txt'):

        rel_path = txt_file.relative_to(src_path)
        bin_file = dest_path / rel_path.with_suffix('.bin')
        bin_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
    
            with open(txt_file, 'r', encoding='utf-8') as f_in, \
                 open(bin_file, 'wb') as f_out:
                
                for line in f_in:
                    hex_str = line.strip()
                    if not hex_str:
                        continue
            
                    raw_bytes = bytes.fromhex(hex_str)
                    f_out.write(raw_bytes)
                    
            print(f"Converted: {rel_path} -> {bin_file.relative_to(dest_path)}")
            
        except ValueError as e:
            print(f"[!] Skipped {rel_path} - Invalid hex data: {e}")
        except Exception as e:
            print(f"[!] Error processing {rel_path}: {e}")

if __name__ == "__main__":
    print("Starting dataset conversion for NIST STS...")
    prepare_nist_dataset()
    print("Done. Output written to 'proc_datasets/'.")
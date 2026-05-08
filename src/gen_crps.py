from pathlib import Path

def generate_crp_streams(chal_path, resp_path, out_xor, out_concat):
    with open(chal_path, 'rb') as fc, open(resp_path, 'rb') as fr:
        chal_bytes = fc.read()
        resp_bytes = fr.read()

    min_len = min(len(chal_bytes), len(resp_bytes))
    chal_bytes = chal_bytes[:min_len]
    resp_bytes = resp_bytes[:min_len]

    xor_result = bytes(c ^ r for c, r in zip(chal_bytes, resp_bytes))
    with open(out_xor, 'wb') as fx:
        fx.write(xor_result)

    concat_result = bytearray()
    for i in range(0, min_len, 4):
        concat_result.extend(chal_bytes[i:i+4])
        concat_result.extend(resp_bytes[i:i+4])
        
    with open(out_concat, 'wb') as fc_out:
        fc_out.write(concat_result)

def main():
    base_dir = Path("proc_datasets")
    crp_dir = Path("crp_datasets") 

    voltages = ["880mV", "800mV", "720mV", "660mV", "600mV", "583mV", "540mV", "530mV", "477mV"]
    chal_file = base_dir / "input_1K.bin"

    if not chal_file.exists():
        print(f"Missing challenge file: {chal_file}")
        return

    for v in voltages:
        for chip in ["chip1.bin", "chip2.bin", "chip3.bin"]:
            resp_file = base_dir / v / chip
            if not resp_file.exists(): continue
            
            out_dir = crp_dir / v
            out_dir.mkdir(parents=True, exist_ok=True)
            
            out_xor = out_dir / f"{chip.replace('.bin', '')}_CRP_XOR.bin"
            out_concat = out_dir / f"{chip.replace('.bin', '')}_CRP_Concat.bin"
            
            generate_crp_streams(chal_file, resp_file, out_xor, out_concat)
            print(f"Generated CRP datasets for {v} - {chip}")

if __name__ == "__main__":
    main()
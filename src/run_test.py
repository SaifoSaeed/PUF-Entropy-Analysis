import os
import subprocess
import json
import argparse
import re
from pathlib import Path

def clean_sts_output_dir():
    target_dir = os.path.join(WINDOWS_STS_ROOT, "experiments", "AlgorithmTesting")

    required_subdirs = [
        "Frequency", "BlockFrequency", "CumulativeSums", "Runs",
        "LongestRun", "Rank", "FFT", "NonOverlappingTemplate",
        "OverlappingTemplate", "Universal", "ApproximateEntropy",
        "RandomExcursions", "RandomExcursionsVariant", "Serial", "LinearComplexity"
    ]

    os.makedirs(target_dir, exist_ok=True)
    
    for subdir in required_subdirs:
        os.makedirs(os.path.join(target_dir, subdir), exist_ok=True)    

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".txt"):
                try:
                    os.remove(os.path.join(root, file))
                except Exception as e:
                    pass

def parse_nist_report():
    base_dir = os.path.join(WINDOWS_STS_ROOT, "experiments", "AlgorithmTesting")
    master_path = os.path.join(base_dir, "finalAnalysisReport.txt")

    master_status = {}
    if os.path.exists(master_path):
        with open(master_path, 'r') as f:
            parsing = False
            for line in f:
                if "PROPORTION" in line:
                    parsing = True; continue
                if parsing and line.strip().startswith("-"): continue
                if parsing and line.strip():
                    parts = line.split()
                    if len(parts) >= 12:
                        prop_idx = next((i for i, p in enumerate(parts) if '/' in p), -2)
                        test_name = " ".join(parts[prop_idx + 1:]).replace('*', '').strip()
                        prop = parts[prop_idx].replace('*', '')
                        
                        key = test_name
                        c = 1
                        while key in master_status:
                            key = f"{test_name}_{c}"; c += 1
                        master_status[key] = prop

    if not master_status:
        return {"error": "Master report failed to generate."}

    extracted_floats = {}
    float_pattern = r'([01]?\.\d+(?:[eE][-+]?\d+)?)'    #Thank God AI exists for regex.
    test_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    for test_name in test_dirs:
        res_path = os.path.join(base_dir, test_name, "results.txt")
        if not os.path.exists(res_path): continue
        
        with open(res_path, 'r') as f: 
            content = f.read()

        p_values = re.findall(rf'p[-_]?value\s*=\s*{float_pattern}', content, re.IGNORECASE)
        if not p_values:
            for line in content.split('\n'):
                if not line.strip() or line.strip().startswith("-") or "p-value" in line.lower():
                    continue
                floats = re.findall(rf'\b{float_pattern}\b', line)
                if floats: p_values.append(floats[-1])

        if p_values:
            if len(p_values) == 1:
                extracted_floats[test_name] = float(p_values[0])
            else:
                for i, p in enumerate(p_values, 1):
                    extracted_floats[f"{test_name}_{i}"] = float(p)


    final_numeric_results = {}
    for test, prop in master_status.items():
        if test in extracted_floats:
            final_numeric_results[test] = extracted_floats[test]
        else:
            if prop == "0/1":
            
                final_numeric_results[test] = 0.0
            elif prop == "1/1":
            
                final_numeric_results[test] = 1.0

    return final_numeric_results

def run_nist_on_file(cygwin_file_path, actual_bits):
    clean_sts_output_dir()
    
    CYGWIN_STS_DIR = "/cygdrive/c/cygwin64/sts-2_1_2"

    safe_bits = actual_bits - 8 
    assess_cmd = f"cd {CYGWIN_STS_DIR} && ./assess.exe {safe_bits}"
    
    input_sequence = [
        "0",                 
        cygwin_file_path,    
        "1",                 
        "0",                 
        str(STREAMS),        
        "1"                  
    ]
    input_cmds = "\n".join(input_sequence) + "\n"

    process = subprocess.Popen(
        [WINDOWS_CYGWIN_BASH, "-lc", assess_cmd],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='replace',
        cwd=WINDOWS_STS_ROOT 
    )

    try:
        stdout, stderr = process.communicate(input=input_cmds, timeout=600)
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Timeout"}

    results = parse_nist_report()
    
    if "error" in results:
        print(f"\n[-] {results['error']}")
    
        if "debug_dump" in results:
            print("\n================== FREQUENCY RESULTS.TXT DUMP ==================")
            print(results["debug_dump"][:1000])
            print("================================================================\n")
        else:
            print("\n================== STS TERMINAL LOG ==================")
            print("\n".join(stdout.splitlines()[-20:]))
            print("======================================================\n")
            
    return results

def main():
    master_results = {}
    windows_root = Path(WINDOWS_DATASET_ROOT)

    if not windows_root.exists():
        print(f"Error: {WINDOWS_DATASET_ROOT} does not exist.")
        return

    bin_files = list(windows_root.rglob("*.bin"))

    print(f"Found {len(bin_files)} binary files to process.")

    for i, bin_file in enumerate(bin_files, 1):
        file_size_bytes = os.path.getsize(bin_file)
        file_size_bits = file_size_bytes * 8
        
        rel_path = bin_file.relative_to(windows_root)
        cygwin_file_path = f"{CYGWIN_DATASET_ROOT}/{rel_path.as_posix()}"
        
        print(f"[{i}/{len(bin_files)}] Testing: {rel_path} (n={file_size_bits}) ... ", end="", flush=True)
    
        file_results = run_nist_on_file(cygwin_file_path, file_size_bits)
        
        if "error" in file_results:
            print(f"FAILED ({file_results['error']})")
        else:
            print(f"DONE ({len(file_results)} metrics extracted)")
            
        master_results[str(rel_path)] = file_results

    with open(f"{DF_PATH}/results.json", "w") as f:
        json.dump(master_results, f, indent=4)
        
    print("\nAll tests complete. Results saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Target dataframe path")
    args = parser.parse_args()
    
    DF_PATH = "proc_datasets"
    
    if args.path:
        DF_PATH = args.path

    WINDOWS_CYGWIN_BASH = r"C:\cygwin64\bin\bash.exe"
    WINDOWS_STS_ROOT    = r"C:\cygwin64\sts-2_1_2"

    CYGWIN_STS_ASSESS   = "/cygdrive/c/cygwin64/sts-2_1_2/assess"
    CYGWIN_DATASET_ROOT = f"/cygdrive/c/Users/jmorp/OneDrive/Desktop/Projects/HS-Assign3/{DF_PATH}"

    WINDOWS_DATASET_ROOT = rf"C:\Users\jmorp\OneDrive\Desktop\Projects\HS-Assign3\{DF_PATH}"

    BIT_LENGTH = "1000000" 
    STREAMS    = "1"       

    main()
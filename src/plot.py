import json
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def plot_head_to_head(RESULTS_PATH, output_dir, json_path="results.json"):
    print("Loading NIST STS Data...")
    with open(f"{RESULTS_PATH}/{json_path}", 'r') as f:
        raw_data = json.load(f)

    records = []
    
    for filepath, tests in raw_data.items():
        if "error" in tests:
            continue
            
        if "input_" in filepath or "across_" in filepath:
            continue 
            
        chip_match = re.search(r'(chip[123])', filepath)
        if not chip_match:
            continue
        chip = chip_match.group(1).capitalize()
        
        for test_name, p_value in tests.items():
        
            base_test = re.sub(r'_[0-9]+$', '', test_name)
            
            records.append({
                "Chip": chip,
                "Test_Family": base_test,
                "Passed": 1 if float(p_value) >= 0.01 else 0
            })

    df = pd.DataFrame(records)

    agg_df = df.groupby(['Test_Family', 'Chip'])['Passed'].mean().reset_index()
    agg_df['Pass_Rate_Pct'] = agg_df['Passed'] * 100

    plt.figure(figsize=(14, 10))
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(
        data=agg_df, 
        y='Test_Family', 
        x='Pass_Rate_Pct', 
        hue='Chip', 
        palette={"Chip1": "#4472C4", "Chip2": "#ED7D31", "Chip3": "#A5A5A5"}
    )

    plt.title('Head-to-Head Cryptographic Profiling: Chip 1 vs. Chip 2 vs. Chip 3', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Average Pass Rate (%) Across All Supply Voltages', fontsize=12, fontweight='bold')
    plt.ylabel('NIST SP 800-22 Statistical Test', fontsize=12, fontweight='bold')

    plt.xlim(0, 110)

    for container in ax.containers:
        ax.bar_label(
            container, 
            fmt='%.1f%%', 
            padding=3, 
            fontsize=9, 
            color='black'
        )

    plt.legend(title='Physical Silicon', title_fontsize='11', loc='lower right')
    
    plt.tight_layout()
    output_filename = f"{output_dir}/H2H_Comparison.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
    
    print(f"Success. Plot saved to '{output_filename}'.")

def load_and_clean_data(json_path="results.json"):
    with open(json_path, 'r') as f:
        raw_data = json.load(f)

    records = []
    for filepath, tests in raw_data.items():
        if "error" in tests:
            continue
            
        file_category = "Hardware PUF"
        if "input_" in filepath:
            file_category = "LFSR Baseline"
        elif "across_" in filepath:
            file_category = "Mixed Voltage"

        for test_name, p_value in tests.items():
            base_test = re.sub(r'_[0-9]+$', '', test_name)
            
            records.append({
                "File": filepath.replace('\\', ' | ').replace('.bin', ''),
                "Category": file_category,
                "Base_Test": base_test,
                "Sub_Test": test_name,
                "P_Value": float(p_value),
                "Passed": 1 if float(p_value) >= 0.01 else 0
            })
            
    return pd.DataFrame(records)

def plot_overall_pass_rates(df, output_dir):
    plt.figure(figsize=(14, 10))
    
    file_pass_rates = df.groupby(['File', 'Category'])['Passed'].mean().reset_index()
    file_pass_rates['Pass_Rate_Pct'] = file_pass_rates['Passed'] * 100
    file_pass_rates = file_pass_rates.sort_values('Pass_Rate_Pct', ascending=False)

    sns.barplot(
        data=file_pass_rates, 
        x='Pass_Rate_Pct', 
        y='File', 
        hue='Category',
        dodge=False,
        palette={"LFSR Baseline": "#4472C4", "Hardware PUF": "#C00000", "Mixed Voltage": "#7030A0"}
    )

    plt.title('Overall NIST STS Pass Rates by Dataset', fontsize=16, pad=20)
    plt.xlabel('Percentage of Tests Passed (P-value ≥ 0.01)', fontsize=12)
    plt.ylabel('Dataset', fontsize=12)
    plt.axvline(99.0, color='green', linestyle='--', label='Cryptographic Standard (99%)')
    plt.legend(title='Data Source')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '1_Overall_Pass_Rates.png'), dpi=300)
    plt.close()

def plot_test_failure_profile(df, output_dir):
    plt.figure(figsize=(12, 8))
    
    hw_df = df[df['Category'] == 'Hardware PUF']
    test_fail_rates = hw_df.groupby('Base_Test')['Passed'].apply(lambda x: (1 - x.mean()) * 100).reset_index()
    test_fail_rates.rename(columns={'Passed': 'Fail_Rate_Pct'}, inplace=True)
    test_fail_rates = test_fail_rates.sort_values('Fail_Rate_Pct', ascending=False)

    sns.barplot(data=test_fail_rates, x='Fail_Rate_Pct', y='Base_Test', color='#d9534f')
    
    plt.title('Hardware Cryptographic Vulnerability Profile\n(Failure Rate by Test Category)', fontsize=14, pad=15)
    plt.xlabel('Failure Rate (%) across all Silicon datasets', fontsize=12)
    plt.ylabel('NIST SP 800-22 Test Family', fontsize=12)
    
    for i, v in enumerate(test_fail_rates['Fail_Rate_Pct']):
        plt.text(v + 1, i + 0.15, f"{v:.1f}%", color='black', fontsize=10)

    plt.xlim(0, 110)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '2_Failure_Profile.png'), dpi=300)
    plt.close()

def plot_diagnostic_heatmap(df, output_dir):
    plt.figure(figsize=(16, 12))
    
    pivot_df = df.pivot_table(
        index='File', 
        columns='Base_Test', 
        values='Passed', 
        aggfunc='mean'
    ) * 100

    pivot_df = pivot_df.sort_index(ascending=False)

    sns.heatmap(
        pivot_df, 
        cmap='RdYlGn', 
        annot=True, 
        fmt=".0f", 
        linewidths=.5, 
        cbar_kws={'label': 'Pass Rate (%)'}
    )
    
    plt.title('Diagnostic Heatmap: Pass Rates by Dataset & Test Category', fontsize=16, pad=20)
    plt.xlabel('NIST Test Family', fontsize=12)
    plt.ylabel('Dataset', fontsize=12)
    

    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3_Diagnostic_Heatmap.png'), dpi=300)
    plt.close()

def main(RESULTS_PATH):
    print("Loading and aggregating NIST results...")
    output_directory = f"{RESULTS_PATH}/nist_plots"
    os.makedirs(output_directory, exist_ok=True)
    
    df = load_and_clean_data(f"{RESULTS_PATH}/results.json")
    
    print(f"Found {len(df)} discrete test evaluations.")
    print("Generating Plot 1: Overall Pass Rates...")
    plot_overall_pass_rates(df, output_directory)
    
    print("Generating Plot 2: Hardware Failure Profile...")
    plot_test_failure_profile(df, output_directory)
    
    print("Generating Plot 3: Diagnostic Heatmap...")
    plot_diagnostic_heatmap(df, output_directory)

    print("Generating H2H Plot...")
    plot_head_to_head(RESULTS_PATH, output_directory)
    
    print(f"Success. Visualizations saved to '{output_directory}/'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Target dataframe path")
    args = parser.parse_args()
    
    if args.path:
        RESULTS_PATH = args.path
        
    main(RESULTS_PATH)
    
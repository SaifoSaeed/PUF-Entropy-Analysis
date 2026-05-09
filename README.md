# PUF Entropy Analysis

This repository contains the dataset, source code, and evaluation results for the randomness analysis of a 22nm FDSOI DCDC Ring Oscillator Physically Unclonable Function (PUF). The evaluation is conducted using the NIST SP 800-22 statistical test suite to assess spatial bias, steady-state entropy, and architectural resilience under varying supply voltages (477mV to 880mV).

## Repository Structure

```text
PUF-Entropy-Analysis/
├── crp_datasets/   # Formatted Challenge-Response Pairs (CRPs) for NIST evaluation
├── datasets/       # Raw baseline data (datasets.zip)
├── proc_datasets/  # Processed raw hardware silicon responses
├── src/            # Python automation scripts (parsing, dataset generation, plotting)
├── xor_datasets/   # Inter-chip XOR datasets for uniqueness evaluation
├── Makefile        # Execution commands
└── .gitignore
```

## Methodology

The evaluation isolates the true cryptographic entropy of the raw silicon responses by generating multiple data pipelines:

1. **Raw Processing:** Extracts the raw responses from various chips under voltages ranging from 477mV to 880mV.
2. **Inter-Chip Uniqueness (Spatial Entropy):** XORs the outputs of different chips under the exact same challenges to test manufacturing variation randomness.
3. **Strict Avalanche Criterion (SAC):** Evaluates the diffuseness of the PUF by formatting CRPs to test the non-linear relationship between inputs and outputs.

## Key Findings

Based on the extraction of over 6,000 metrics from the NIST SP 800-22 suite, the physical hardware exhibits the following properties:

* **Severe Spatial Bias:** The raw outputs exhibit highly deterministic behavior, suffering a 100% failure rate in transition density tests (Runs, Longest Run, Approximate Entropy).
* **Physical, Not Algorithmic Bias:** Despite the density failures, the sequences passed the Linear Complexity test (>96%), confirming the bias is purely physical and not the result of simple structural linearity.
* **Supply Voltage Volatility:** The metastable states of the oscillators proved hyper-sensitive to DC/DC supply scaling, drastically altering the entropy profiles across the voltage sweeps.

## Security Applications

Based on the hardware sensitivities and randomness profiles, the tested silicon dies map to specific security applications:
* **Chip 1 (Low-Cost Device Fingerprinting):** Consistently exhibited a heavily skewed, repeatable bitstream. This stable spatial bias serves as a unique silicon barcode, ideal for supply chain tracking in low-resource IoT environments.
* **Chip 2 (Hardware Tamper & Fault-Injection Sensing):** Demonstrated extreme volatility to supply line fluctuations. This hyper-sensitivity to the integrated DC/DC converter makes it an excellent hardware tripwire to detect active side-channel attacks or voltage-glitching.
* **Chip 3 (Cryptographic Key Generation):** Exhibited the most balanced frequency metrics. With post-processing (Von Neumann Corrector and Fuzzy Extractor), its baseline entropy can be utilized for seeding symmetric/asymmetric cryptographic engines (AES/ECC).

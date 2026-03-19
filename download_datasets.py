#!/usr/bin/env python3
"""
Download and prepare all 3 real datasets for maximum accuracy
"""

import os
import sys
import urllib.request
import zipfile
import subprocess

print("=" * 80)
print("DOWNLOADING REAL DATASETS FOR MAXIMUM ACCURACY")
print("=" * 80)

os.chdir("/Users/vijayreddy/honey pot agent")

# Dataset 1: UCI SMS Spam (Auto-downloads in main script)
print("\n[1/3] UCI SMS Spam Collection")
print("✓ Will be downloaded automatically during training")

# Dataset 2: Kaggle Phishing Email
print("\n[2/3] Kaggle Phishing Email Dataset")
print("Downloading via Kaggle API...")

try:
    # Download using Kaggle API
    result = subprocess.run([
        'kaggle', 'datasets', 'download', '-d', 
        'naserabdullahalam/phishing-email-dataset',
        '--force'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Download complete")
        
        # Unzip
        if os.path.exists('phishing-email-dataset.zip'):
            print("Extracting...")
            with zipfile.ZipFile('phishing-email-dataset.zip', 'r') as zip_ref:
                zip_ref.extractall('.')
            print("✓ Extracted successfully")
            
            # Clean up zip
            os.remove('phishing-email-dataset.zip')
        else:
            print("⚠ Zip file not found, checking if already extracted...")
    else:
        print(f"⚠ Kaggle API error: {result.stderr}")
        print("Will use synthetic email data")
        
except Exception as e:
    print(f"⚠ Error: {e}")
    print("Will use synthetic email data")

# Dataset 3: Mendeley SMS Phishing
print("\n[3/3] Mendeley SMS Phishing Dataset")
print("Downloading from Mendeley...")

try:
    # Download Mendeley dataset
    url = 'https://data.mendeley.com/public-files/datasets/f45bkkt8pr/files/ba2e94de-4bb5-4dcf-aa2b-58f8edefe97c/file_downloaded'
    
    print("Attempting download...")
    urllib.request.urlretrieve(url, 'mendeley_dataset.zip')
    
    # Unzip
    if os.path.exists('mendeley_dataset.zip'):
        print("Extracting...")
        with zipfile.ZipFile('mendeley_dataset.zip', 'r') as zip_ref:
            zip_ref.extractall('mendeley_data')
        print("✓ Extracted successfully")
        os.remove('mendeley_dataset.zip')
    else:
        print("⚠ Download may have failed")
        
except Exception as e:
    print(f"⚠ Error downloading Mendeley: {e}")
    print("Will use synthetic SMS phishing data")

# Check what files we have
print("\n" + "=" * 80)
print("DATASET FILES CHECK")
print("=" * 80)

import glob

print("\nChecking for downloaded files...")
csv_files = glob.glob("*.csv") + glob.glob("mendeley_data/*.csv")
print(f"\nFound {len(csv_files)} CSV files:")
for f in csv_files:
    size = os.path.getsize(f) / 1024  # KB
    print(f"  - {f} ({size:.1f} KB)")

print("\n" + "=" * 80)
print("DOWNLOAD COMPLETE!")
print("=" * 80)
print("\nNext step: Run training with all datasets")
print("Command: python advanced_scam_detector.py")

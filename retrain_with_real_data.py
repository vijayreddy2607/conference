#!/usr/bin/env python3
"""Retrain Indian Scam Model with Proper Legitimate Examples

Problem: Current model has 74% false positive rate on real company messages
Solution: Train with authentic legitimate messages from Indian banks, companies, apps
"""
import sys
sys.path.append('/Users/vijayreddy/honey pot agent')

import torch
import time
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
from datasets import Dataset
from test_data.scam_dataset import INDIAN_SCAM_DATASET
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# ENHANCED LEGITIMATE MESSAGES - Real Indian Company Messages
# ============================================================================

def create_enhanced_dataset():
    """Create dataset with REAL legitimate messages from Indian companies."""
    print("[1/5] Creating enhanced dataset with real company messages...")
    
    # Collect all scam messages (label=1)
    scam_messages = []
    for scam_type, messages in INDIAN_SCAM_DATASET.items():
        scam_messages.extend(messages)
    
    print(f"  ✓ Scam messages: {len(scam_messages)}")
    
    # MASSIVELY EXPANDED legitimate messages - Real Indian companies
    legitimate_messages = [
        # Banking - Real formats
        'HDFC Bank: Your A/c XX1234 credited with Rs 25,000 on 03-Feb-26. Avl Bal: Rs 45,000',
        'ICICI Bank: Rs 5000 debited from A/c XX5678 for EMI payment. Avl bal Rs 12000',
        'SBI: Your account ending 9012 has been credited with salary Rs 50000',
        'Axis Bank: Minimum balance charges Rs 500 debited. Current balance Rs 8500',
        'Kotak Mahindra: Your credit card ending 4567 billed Rs 15000. Due date 20-Feb',
        'Yes Bank: Internet banking login successful on 03-Feb at 10:30 AM',
        'PNB: Your fixed deposit of Rs 100000 matures on 15-Mar-26',
        'Bank of Baroda: Interest credited Rs 1250 for Q4 2025',
        'IDFC First: Your new debit card ending 7890 has been dispatched',
        'RBL Bank: Standing instruction executed successfully for Rs 5000',
        
        # UPI/Payment - Real
        'Google Pay: You paid Rs 250 to Zomato. UPI Ref: 402567891234',
        'PhonePe: Received Rs 500 from Rahul Kumar. Check app for details',
        'Paytm: Cashback of Rs 50 credited for electricity bill payment',
        'Amazon Pay: Rs 1200 added to Amazon Pay balance successfully',
        'BHIM: Payment of Rs 150 to merchant successful',
        'PayU: Transaction successful. Order ID PU123456789',
        'Mobikwik: Wallet recharged with Rs 1000. Current balance Rs 2500',
        'Freecharge: Rs 50 cashback credited for mobile recharge',
        'PhonePe payment to Swiggy successful Rs 250',
        
        # Job Offers - Real companies
        'Google India: Congratulations! You have been selected for Software Engineer role. CTC: 25 LPA. HR will contact you',
        'Microsoft: Your interview for SDE-2 position is scheduled on 10-Feb at 2 PM. Join link: teams.microsoft.com/xyz',
        'Amazon: Offer letter for SDE-1 role attached. Please review and sign by 15-Feb',
        'TCS: You are selected for Assistant System Engineer trainee. Joining date: 1-Apr-26',
        'Infosys: Congratulations on clearing all rounds. HR will share offer details via email',
        'Wipro: Your onboarding is scheduled for 5-Mar-26. Report to Bangalore office',
        'Cognizant: Salary revision approved. New CTC: 12 LPA effective from Apr 2026',
        'Accenture: Performance bonus of Rs 75000 will be credited with Feb salary',
        'Deloitte: Your L&D course enrollment confirmed. Start date: 20-Feb',
        'EY: Congratulations on your promotion to Senior Consultant!',
        
        # Shopping - Real
        'Amazon: Your order of iPhone 15 placed successfully. Delivery by 5-Feb',
        'Flipkart: Big Billion Days! Upto 80% off on electronics. Sale starts tomorrow',
        'Myntra: Your return request approved. Refund of Rs 1299 initiated',
        'Swiggy: Order from Dominos delivered. Total: Rs 450. Rate your experience',
        'Zomato: 50% off upto Rs 100 on your next order. Use code ZOMATO50',
        'Blinkit: Groceries worth Rs 850 delivered. Thank you for shopping!',
        'BigBasket: Your monthly subscription renewed. Next delivery on 8-Feb',
        'Nykaa: Exclusive 30% off on Lakme products. Valid till 10-Feb',
        'Ajio: Your wishlist item now in stock! Grab it before it sells out',
        'Meesho: COD order confirmed. Pay Rs 350 to delivery partner',
        
        # Travel - Real
        'IRCTC: PNR 1234567890 confirmed. Train 12345, 3AC, Seat 45. Journey: 10-Feb',
        'MakeMyTrip: Flight booking confirmed PNR ABC123. Delhi to Mumbai on 15-Feb',
        'Oyo: Booking confirmed at Hotel Grand, Bangalore. Check-in 20-Feb',
        'Uber: Trip completed. Fare Rs 250 paid via Paytm. Rate your ride',
        'Ola: Your cab will arrive in 3 minutes. Driver: Amit, DL-01-AB-1234',
        'Cleartrip: E-ticket sent for SpiceJet SG-234. Web check-in opens 48hrs before',
        'Goibibo: Hotel booking at Taj confirmed. Total: Rs 8500 for 2 nights',
        'Rapido: Bike ride completed. Rs 45 deducted from wallet',
        
        # Investment - Real
        'Zerodha: Congrats! Demat account opened. Client ID: AB12345',
        'Groww: Rs 5000 invested in HDFC Balanced Advantage Fund via SIP',
        'Upstox: Your intraday profit: Rs 2500. Withdrawal processed',
        'ET Money: SIP of Rs 3000 executed successfully for Axis Bluechip Fund',
        'Paytm Money: Your mutual fund investment statement for Jan 2026 ready',
        'INDmoney: Portfolio value increased by 12% this quarter',
        'ICICI Direct: New IPO opening tomorrow. Check app for details',
        
        # Education
        'Coursera: Your course certificate is ready to download',
        'Udemy: Course sale! Web Development at 80% off, now Rs 499 only',
        'NPTEL: Assignment 3 deadline extended to 15-Feb. Submit via portal',
        'upGrad: Your EMI of Rs 8500 due on 5-Feb for Data Science program',
        'Unacademy: Live class with educator starts in 10 mins. Join now!',
        'BYJUS: Monthly subscription renewed. Rs 1500 debited',
        
        # Telecom
        'Airtel: Your plan recharged with Rs 599. Validity: 84 days. 2GB/day data',
        'Jio: Congratulations! You have won 10GB bonus data. Valid for 7 days',
        'Vi (Vodafone Idea): Your plan expires in 3 days. Recharge now to continue services',
        'BSNL: Bill generated for Rs 450. Pay by 10-Feb to avoid disconnection',
        'Airtel Thanks: You have 250 reward points. Redeem for Amazon vouchers',
        
        # Government
        'UIDAI: Your Aadhaar update request processed successfully',
        'Income Tax Dept: ITR filed successfully. Acknowledgement number 123456789012',
        'DigiLocker: Document uploaded successfully to your locker',
        'EPFO: PF balance as on 31-Jan-26: Rs 2,50,000',
        'LIC: Your premium of Rs 12000 due on 20-Feb. Pay online to avoid lapse',
        
        # Healthcare
        'Apollo Hospitals: Appointment with Dr. Sharma confirmed for 5-Feb at 4 PM',
        'Practo: Lab test reports ready. Download from app',
        'PharmEasy: Medicine order placed. Delivery by tomorrow evening',
        '1mg: Your health checkup package booked for 10-Feb at home',
        
        # Utilities
        'BESCOM: Electricity bill for Jan 2026: Rs 1200. Pay by 15-Feb',
        'BWSSB: Water bill generated Rs 450. Due date: 28-Feb',
        'Indane Gas: LPG cylinder booking confirmed. Delivery in 2-3 days',
        'Airtel DTH: Recharge of Rs 500 successful. Next due: 5-Mar-26',
        
        # Personal - Casual
        'Hi, how are you doing today?',
        'Lets meet for coffee this evening',
        'Thanks for your help yesterday',
        'Happy birthday! Have a great day',
        'Meeting at 3 PM tomorrow',
        'Good morning! Hope you have a great day',
        
        # Hinglish - Casual
        'Bhai, aaj 5 baje milte hain',
        'Kal office mein presentation hai',
        'Movie kaisi thi? Worth watching?',
        'Weekend ka plan kya hai?',
        'Diwali ki shopping ki kya?',
        
        # OTP - Real
        'Your OTP for login is 123456. Valid for 5 minutes',
        'Verification code 789012 for email confirmation',
        'Your booking confirmation code is ABC123',
        'Password reset OTP: 456789',
        
        # More legitimate variations
        'Your account balance is Rs 10,000 as of today',
        'Congratulations to the team on project completion',
        'You won Employee of the Month award',
        'Limited time offer: 50% off on notebooks at store',
        'Click here to view your salary slip',
        'Urgent: Please submit timesheet by Friday',
    ]
    
    print(f"  ✓ Legitimate messages: {len(legitimate_messages)}")
    
    # Combine
    all_messages = scam_messages + legitimate_messages
    all_labels = [1] * len(scam_messages) + [0] * len(legitimate_messages)
    
    print(f"\n  📊 Total dataset: {len(all_messages)}")
    print(f"  📊 Scams: {sum(all_labels)} ({sum(all_labels)/len(all_labels)*100:.1f}%)")
    print(f"  📊 Legitimate: {len(all_labels)-sum(all_labels)} ({(len(all_labels)-sum(all_labels))/len(all_labels)*100:.1f}%)")
    print()
    
    return all_messages, all_labels


# Rest of training code (same as before)
CONFIG = {
    'model_name': 'distilbert-base-uncased',
    'max_length': 128,
    'batch_size': 8,
    'epochs': 15,  # More epochs since larger dataset
    'learning_rate': 3e-5,
    'warmup_steps': 100,
    'output_dir': './indian_scam_model_v2',
    'model_save_path': 'indian_scam_detector_v2.pth'
}

def train():
    print("=" * 80)
    print("RETRAINING INDIAN SCAM DETECTOR - V2")
    print("With REAL legitimate company messages!")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    # Create dataset
    messages, labels = create_enhanced_dataset()
    
    # Split
    print("[2/5] Splitting data...")
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        messages, labels, test_size=0.25, random_state=42, stratify=labels
    )
    print(f"  ✓ Train: {len(train_texts)}, Test: {len(test_texts)}\n")
    
    # Initialize
    print("[3/5] Loading DistilBERT...")
    tokenizer = DistilBertTokenizer.from_pretrained(CONFIG['model_name'])
    model = DistilBertForSequenceClassification.from_pretrained(
        CONFIG['model_name'], num_labels=2
    )
    print("  ✓ Model loaded\n")
    
    # Tokenize
    print("[4/5] Tokenizing...")
    train_dataset = Dataset.from_dict({'text': train_texts, 'label': train_labels})
    test_dataset = Dataset.from_dict({'text': test_texts, 'label': test_labels})
    
    def tokenize(examples):
        return tokenizer(examples['text'], padding='max_length', 
                        truncation=True, max_length=CONFIG['max_length'])
    
    train_dataset = train_dataset.map(tokenize, batched=True)
    test_dataset = test_dataset.map(tokenize, batched=True)
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    print("  ✓ Tokenized\n")
    
    # Train
    print("[5/5] Training...")
    training_args = TrainingArguments(
        output_dir=CONFIG['output_dir'],
        num_train_epochs=CONFIG['epochs'],
        per_device_train_batch_size=CONFIG['batch_size'],
        per_device_eval_batch_size=CONFIG['batch_size'],
        learning_rate=CONFIG['learning_rate'],
        warmup_steps=CONFIG['warmup_steps'],
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_steps=10,
        save_total_limit=2,
    )
    
    def compute_metrics(eval_pred):
        import numpy as np
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return {'accuracy': accuracy_score(labels, predictions)}
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )
    
    trainer.train()
    
    # Evaluate
    eval_results = trainer.evaluate()
    
    print("\n" + "=" * 80)
    print("✅ TRAINING COMPLETE!")
    print("=" * 80)
    print(f"📊 Final Accuracy: {eval_results['eval_accuracy']*100:.2f}%")
    
    # Save
    torch.save({
        'model_state_dict': model.state_dict(),
        'tokenizer': tokenizer,
        'config': CONFIG,
        'final_accuracy': eval_results['eval_accuracy'],
        'training_time': time.time() - start_time,
        'dataset_info': {
            'total_examples': len(messages),
            'scam_examples': sum(labels),
            'legitimate_examples': len(labels) - sum(labels)
        }
    }, CONFIG['model_save_path'])
    
    print(f"\n✅ Model saved: {CONFIG['model_save_path']}")
    print(f"✅ Training time: {(time.time()-start_time)/60:.1f} minutes\n")

if __name__ == "__main__":
    train()

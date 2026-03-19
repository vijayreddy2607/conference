"""Train Indian-Specific Binary Scam Detection Model

Fine-tunes DistilBERT specifically on Indian scam patterns:
- 100 Indian scam examples (all types)
- 100+ legitimate Indian messages
- Learns UPI, ₹, Indian banks, Hinglish patterns

This should push binary detection from 91% → 95%+!
"""
import sys
sys.path.append('/Users/vijayreddy/honey pot agent')

import torch
import time
from datetime import datetime
from pathlib import Path
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
# CONFIGURATION
# ============================================================================

CONFIG = {
    'model_name': 'distilbert-base-uncased',
    'max_length': 128,
    'batch_size': 8,  # Larger since small dataset
    'epochs': 10,  # More epochs for small dataset
    'learning_rate': 3e-5,
    'warmup_steps': 50,
    'output_dir': './indian_scam_model',
    'model_save_path': 'indian_scam_detector.pth'
}

print("=" * 80)
print("INDIAN SCAM BINARY DETECTION MODEL - TRAINING")
print("=" * 80)
print(f"Model: {CONFIG['model_name']}")
print(f"Batch Size: {CONFIG['batch_size']}")
print(f"Epochs: {CONFIG['epochs']}")
print("=" * 80)
print()


# ============================================================================
# PREPARE DATASET
# ============================================================================

def create_indian_dataset():
    """Create balanced dataset of Indian scams + legitimate messages."""
    print("[1/5] Creating Indian scam dataset...")
    
    # Collect all scam messages (label=1)
    scam_messages = []
    for scam_type, messages in INDIAN_SCAM_DATASET.items():
        scam_messages.extend(messages)
    
    print(f"  ✓ Scam messages: {len(scam_messages)}")
    
    # Create legitimate Indian messages (label=0)
    legitimate_messages = [
        # Personal conversations
        "Hi, how are you doing today?",
        "Let's meet for coffee this evening",
        "Thanks for your help with the project",
        "Happy birthday! Have a wonderful day",
        "Can you send me the report by EOD?",
        "Meeting at 3 PM in conference room",
        "Good morning! Hope you have a great day",
        "Congratulations on your promotion!",
        "See you tomorrow at the office",
        "Let's catch up over lunch this weekend",
        
        # Indian context legitimate
        "Bhai, aaj 5 baje milte hain",
        "Ma ka khana bahut accha tha",
        "Kal office mein presentation hai",
        "Diwali ki chutti kab hai?",
        "IPL match dekh rahe ho?",
        "Chai peene chalte hain",
        "Weekend plan kya hai bro?",
        "Birthday party mein aa rahe ho?",
        "Train ticket book kar liya?",
        "Movie kaisi thi?",
        
        # Banking legitimate (real notifications)
        "Your SBI account credited with Rs 5000",
        "HDFC Bank: Thank you for choosing us",
        "ICICI: Your payment was successful",
        "Paytm cashback credit Rs 50",
        "PhonePe payment to merchant successful",
        "Google Pay: You sent Rs 100 to Mom",
        "Thank you for shopping with Amazon",
        "Flipkart order #12345 delivered",
        "Swiggy: Your order is on the way",
        "Ola ride completed. Rs 150 paid",
        
        # Work messages
        "Team meeting scheduled for tomorrow 10 AM",
        "Please review the attached document",
        "Weekly standup at 9:30 AM",
        "Deadline extended to next Friday",
        "Great work on the presentation!",
       "Can you share the updated spreadsheet?",
        "OOO tomorrow, will respond on Monday",
        "Thanks for the quick turnaround",
        "Conference call in 10 minutes",
        "Please approve the PR when you get a chance",
        
        # Social/Family
        "Mom: Don't forget to take your medicine",
        "Dad: What time are you coming home?",
        "Sister: Can you pick me up from school?",
        "Friend: Party tonight at 8 PM, you coming?",
        "Colleague: Want to grab lunch?",
        "Neighbor: Package delivered at my door for you",
        "Doctor: Appointment confirmed for tomorrow 3 PM",
        "School: Parent-teacher meeting next week",
        "Gym: Your membership expires in 30 days",
        "Library: Book due date reminder",
        
        # Shopping/Services
        "Amazon: Your order has been shipped",
        "Flipkart: Product will be delivered tomorrow",
        "Zomato: Your order is being prepared",
        "BookMyShow: Ticket booked successfully",
        "Uber: Driver is 2 mins away",
        "Airtel: Your bill is Rs 599 this month",
        "Netflix: New season of your show available",
        "Spotify: New playlist recommendations",
        "Google: Security alert - new sign-in detected",
        "WhatsApp: New privacy policy update",
        
        # OTP/Verification (legitimate)
        "Your OTP is 123456. Valid for 5 minutes",
        "Verification code: 789012 for login",
        "Your booking confirmation code is ABC123",
        "Password reset OTP: 456789",
        "Email verification code: 321654",
        
        # Informational
        "Weather alert: Heavy rain expected today",
        "Traffic update: Road blocked on highway",
        "Election reminder: Vote on Saturday",
        "COVID vaccination slot available at 2 PM",
        "Water supply will be interrupted from 10-2",
        "Power cut scheduled for maintenance 12-4 PM",
        "Gas cylinder delivery on Wednesday",
        "Garbage collection truck arriving soon",
        "Society meeting at 6 PM in clubhouse",
        "Maintenance charges due by 10th",
        
        # Education
        "Class postponed to next week",
        "Assignment submission deadline Friday",
        "Exam results announced tomorrow",
        "New semester starts Monday",
        "Library books due this week",
        "College fest registrations open",
        "Workshop on Saturday morning",
        "Guest lecture at 4 PM today",
        "Scholarship applications open",
        "Placement drive next month",
        
        # Healthcare
        "Prescription refill ready for pickup",
        "Lab test results available online",
        "Health checkup due next month",
        "Vaccination record updated",
        "Insurance claim approved",
        "Doctor appointment rescheduled",
        "Medicine reminder: Take at 8 PM",
        "Gym membership renewal due",
        "Yoga class starts tomorrow",
        "Health insurance premium due",
        
        # Financial (legitimate)
        "Mutual fund statement available",
        "Credit card bill generated Rs 5000",
        "Fixed deposit matured",
        "Insurance premium paid successfully",
        "Tax payment confirmation",
        "Salary credited to your account",
        "Bonus payment received",
        "Dividend credited Rs 1000",
        "Investment SIP processed",
        "Loan EMI deducted Rs 10000"
    ]
    
    print(f"  ✓ Legitimate messages: {len(legitimate_messages)}")
    
    # Combine
    all_messages = scam_messages + legitimate_messages
    all_labels = [1] * len(scam_messages) + [0] * len(legitimate_messages)
    
    print(f"\n  📊 Total dataset size: {len(all_messages)}")
    print(f"  📊 Scams: {sum(all_labels)} ({sum(all_labels)/len(all_labels)*100:.1f}%)")
    print(f"  📊 Legitimate: {len(all_labels)-sum(all_labels)} ({(len(all_labels)-sum(all_labels))/len(all_labels)*100:.1f}%)")
    print()
    
    return all_messages, all_labels


def prepare_data(messages, labels):
    """Split into train/test sets."""
    print("[2/5] Splitting data...")
    
    # 70-30 split
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        messages, labels,
        test_size=0.3,
        random_state=42,
        stratify=labels
    )
    
    print(f"  ✓ Training: {len(train_texts)} samples")
    print(f"  ✓ Testing: {len(test_texts)} samples")
    print()
    
    return train_texts, train_labels, test_texts, test_labels


def create_datasets(train_texts, train_labels, test_texts, test_labels, tokenizer):
    """Create HuggingFace datasets."""
    print("[3/5] Tokenizing...")
    
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            padding='max_length',
            truncation=True,
            max_length=CONFIG['max_length']
        )
    
    train_dataset = Dataset.from_dict({
        'text': train_texts,
        'label': train_labels
    })
    
    test_dataset = Dataset.from_dict({
        'text': test_texts,
        'label': test_labels
    })
    
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)
    
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    
    print("  ✓ Tokenization complete")
    print()
    
    return train_dataset, test_dataset


def compute_metrics(eval_pred):
    """Compute accuracy."""
    import numpy as np
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = accuracy_score(labels, predictions)
    return {'accuracy': accuracy}


# ============================================================================
# TRAINING
# ============================================================================

def train_model():
    """Train the Indian scam detection model."""
    start_time = time.time()
    
    # Prepare data
    messages, labels = create_indian_dataset()
    train_texts, train_labels, test_texts, test_labels = prepare_data(messages, labels)
    
    # Initialize
    print("[4/5] Initializing model...")
    tokenizer = DistilBertTokenizer.from_pretrained(CONFIG['model_name'])
    model = DistilBertForSequenceClassification.from_pretrained(
        CONFIG['model_name'],
        num_labels=2
    )
    print("  ✓ Model initialized")
    print()
    
    # Create datasets
    train_dataset, test_dataset = create_datasets(
        train_texts, train_labels, test_texts, test_labels, tokenizer
    )
    
    # Training arguments
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
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )
    
    # Train
    print("[5/5] Training...")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    trainer.train()
    
    # Evaluate
    eval_results = trainer.evaluate()
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"📊 Final Accuracy: {eval_results['eval_accuracy']*100:.2f}%")
    
    # Detailed metrics
    import numpy as np
    predictions = trainer.predict(test_dataset)
    pred_labels = np.argmax(predictions.predictions, axis=-1)
    
    print("\n" + classification_report(
        test_labels,
        pred_labels,
        target_names=['Legitimate', 'Scam'],
        digits=4
    ))
    
    print("Confusion Matrix:")
    cm = confusion_matrix(test_labels, pred_labels)
    print(cm)
    print(f"\nTrue Negatives: {cm[0][0]} | False Positives: {cm[0][1]}")
    print(f"False Negatives: {cm[1][0]} | True Positives: {cm[1][1]}")
    
    # Save model
    print("\n" + "=" * 80)
    print("SAVING MODEL")
    print("=" * 80)
    
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
    
    print(f"✅ Model saved to: {CONFIG['model_save_path']}")
    print(f"✅ Training time: {(time.time()-start_time)/60:.1f} minutes")
    
    if eval_results['eval_accuracy'] >= 0.95:
        print("\n🎉 SUCCESS! Achieved 95%+ accuracy!")
    else:
        print(f"\n📊 Achieved {eval_results['eval_accuracy']*100:.1f}% accuracy")
    
    return model, tokenizer, eval_results


if __name__ == "__main__":
    print("\n🚀 Starting Indian scam detection model training...\n")
    model, tokenizer, results = train_model()
    print("\n✅ All done! Model ready for production.\n")

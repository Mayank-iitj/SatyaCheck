import json
import os
from datasets import load_dataset

def main():
    print("Loading 'ucirvine/sms_spam' dataset from Hugging Face...")
    try:
        dataset = load_dataset("ucirvine/sms_spam")
        train_data = dataset['train']
        
        financial_keywords = ['stock', 'invest', 'crypto', 'profit', 'returns', 'guaranteed', 'broker', 'trade', 'bonus', 'cash', 'earn', 'prize', 'won', 'claim']
        
        scam_messages = []
        for item in train_data:
            label = item.get('label')
            sms_text = item.get('sms', '')
            
            # Standard label is 1 for spam
            if label == 1:
                if any(kw in sms_text.lower() for kw in financial_keywords):
                    scam_messages.append(sms_text.strip())
                    
        print(f"Found {len(scam_messages)} real financial spam/scam examples in dataset.")
        
        # Save to JSON file
        out_path = os.path.join(os.path.dirname(__file__), 'financial_scams_db.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(scam_messages, f, indent=2, ensure_ascii=False)
            
        print(f"Saved real dataset examples to: {out_path}")
        
    except Exception as e:
        print(f"Error fetching dataset: {str(e)}")

if __name__ == "__main__":
    main()

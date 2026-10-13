import os
import re
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer

def inject_and_train():
    print("=== STARTING ADVANCED STAGE 2: MATHEMATICAL THRESHOLD TEST ===")
    
    linux_raw_path = os.path.join("raw_logs", "linux_2k.log")
    openstack_raw_path = os.path.join("raw_logs", "openstack_normal.log")
    
    with open(linux_raw_path, 'r', encoding='utf-8') as f:
        linux_clean = f.read()
    with open(openstack_raw_path, 'r', encoding='utf-8') as f:
        openstack_clean = f.read()
        
    print("[+] Loading baseline data arrays...")
    
    # Target anomalies that are structurally unique from standard repeating logs
    malicious_security_incident = (
        "Jun 14 15:30:45 ubuntu sshd: ALERT - EXPLOIT ATTEMPT - RCE Buffer Overflow payload\n"
        "Jun 14 15:31:00 ubuntu combat: CRITICAL - Root privileges bypassed via exploit script\n"
    )
    critical_infrastructure_crash = (
        "2026-06-14 15:45:12.999 23482 FATAL nova.compute.manager KERNEL PANIC terminated compute node\n"
        "2026-06-14 15:45:13.102 23482 CRITICAL nova.api HARDWARE FAILURE corrupted storage sector\n"
    )
    
    linux_corrupted = linux_clean + malicious_security_incident
    openstack_corrupted = openstack_clean + critical_infrastructure_crash
    
    filters = [
        (r'(\d+)', '<NUM>'), (r'(\d+\.\d+\.\d+\.\d+)', '<IP>'),
        (r'(0x[0-9a-fA-F]+)', '<HEX>'), (r'(/[a-zA-Z0-9_\-\.]+)+', '<PATH>')
    ]
    
    def mask_text(text):
        for regex, token in filters:
            text = re.sub(regex, token, text)
        return re.sub(r'\s+', ' ', text).strip()

    parsed_data = []
    
    for line in linux_corrupted.strip().split('\n'):
        tokens = line.split(' ')
        if len(tokens) >= 5:
            content = " ".join(tokens[4:])
            parsed_data.append({"Source": "Linux_Auth", "Raw_Content": content, "Event_Template": mask_text(content)})
            
    for line in openstack_corrupted.strip().split('\n'):
        tokens = line.split(' ')
        if len(tokens) >= 4:
            content = " ".join(tokens[3:])
            parsed_data.append({"Source": "OpenStack_Cloud", "Raw_Content": content, "Event_Template": mask_text(content)})

    df_combined = pd.DataFrame(parsed_data)
    
    print("[+] Building TF-IDF matrix profiles...")
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df_combined['Event_Template'])
    
    print("[+] Training Isolation Forest and evaluating Continuous Decision Scores...")
    # Auto calculation lets trees branch natively based on sample density anomalies
    model = IsolationForest(contamination='auto', random_state=42)
    model.fit(X.toarray())
    
    # Obtain the raw continuous outlier distance score
    # Negative scores indicate structural anomalies out of bounds
    raw_scores = model.decision_function(X.toarray())
    df_combined['Raw_Anomaly_Score'] = raw_scores
    
    # Mark anything strictly below zero threshold boundary as an anomaly
    df_combined['Is_Anomaly'] = df_combined['Raw_Anomaly_Score'].apply(lambda x: 1 if x < 0 else 0)
    anomalies = df_combined[df_combined['Is_Anomaly'] == 1]
    
    output_matrix = os.path.join("processed_logs", "ml_analyzed_logs.csv")
    df_combined.to_csv(output_matrix, index=False)
    
    print(f"\n[✓] Analysis Matrix successfully exported to: {output_matrix}")
    print(f"[⚠️] CRITICAL SECURITY/INFRASTRUCTURE ALERTS DETECTED: {len(anomalies)} lines isolated!")
    
    print("\n* Reviewing Isolated Structural Abnormalities:")
    # Drop completely identical log entries from view to see the true unique deviations
    unique_anomalies = anomalies.drop_duplicates(subset=['Event_Template'])
    for idx, row in unique_anomalies.head(5).iterrows():
        print(f"  -> [{row['Source']}] Score: {row['Raw_Anomaly_Score']:.4f} | \"{row['Raw_Content'][:85]}...\"")
        
    print("\n=== STAGE 2 ENGINE EVALUATION RUN REPLICATED SUCCESSFUL ===")

if __name__ == "__main__":
    inject_and_train()

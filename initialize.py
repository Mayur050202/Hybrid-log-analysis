import os
import re
import pandas as pd

def initialize_project():
    folders = ["data", "raw_logs", "processed_logs", "src", "templates"]
    print("=== STEP 1: INITIALIZING FOLDER ARCHITECTURE ===")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"[?] Verified Folder: {folder}")
        
    print("\n=== STEP 2: GENERATING LOCAL LOG BENCHMARKS ===")
    linux_raw = os.path.join("raw_logs", "linux_2k.log")
    openstack_raw = os.path.join("raw_logs", "openstack_normal.log")

    linux_sample_data = (
        "Jun 14 15:16:01 ubuntu sshd: Invalid user admin from 192.168.1.50 port 54321 ssh2\n"
        "Jun 14 15:16:05 ubuntu sshd: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=192.168.1.50\n"
        "Jun 14 15:17:10 ubuntu sshd: Accepted password for root from 10.0.0.4 port 38291 ssh2\n"
        "Jun 14 15:18:22 ubuntu combat: User root changed permissions on /etc/shadow\n"
        "Jun 14 15:20:01 ubuntu sshd: Invalid user anonymous from 172.16.4.22 port 9999 ssh2\n"
    ) * 400

    openstack_sample_data = (
        "2026-06-14 15:16:01.234 23482 INFO nova.osapi_compute.wsgi.server [req-82f3-abcd] 10.0.0.1 \"GET /v2.1/servers HTTP/1.1\" status: 200 len: 1240\n"
        "2026-06-14 15:16:05.849 23482 ERROR nova.compute.manager [req-91a2-bcde] Instance id=inst-93a82f failed to spawn on compute node\n"
        "2026-06-14 15:17:00.111 23482 INFO nova.osapi_compute.wsgi.server [req-74d1-efgh] 10.0.0.5 \"POST /v2.1/flavors HTTP/1.1\" status: 201 len: 450\n"
        "2026-06-14 15:19:33.002 23482 WARNING nova.metadata.wsgi [req-1234-xyz] Missing metadata service mapping for instance id=inst-93a82f\n"
    ) * 500

    with open(linux_raw, 'w', encoding='utf-8') as f:
        f.write(linux_sample_data)
    print(f"[?] Local benchmark synthesized: {linux_raw}")

    with open(openstack_raw, 'w', encoding='utf-8') as f:
        f.write(openstack_sample_data)
    print(f"[?] Local benchmark synthesized: {openstack_raw}")

    print("\n=== STEP 3: EXECUTING STAGE 1 TEMPLATE EXTRACTION ===")
    filters = [
        (r'(\d+)', '<NUM>'), (r'(\d+\.\d+\.\d+\.\d+)', '<IP>'),
        (r'(0x[0-9a-fA-F]+)', '<HEX>'), (r'(/[a-zA-Z0-9_\-\.]+)+', '<PATH>'),
        (r'(?<=id=)[a-zA-Z0-9\-]+', '<ID>')
    ]
    
    def mask_text(text):
        for regex, token in filters:
            text = re.sub(regex, token, text)
        return re.sub(r'\s+', ' ', text).strip()

    if os.path.exists(linux_raw):
        parsed = []
        with open(linux_raw, 'r', encoding='utf-8') as f:
            for line in f:
                tokens = line.strip().split(' ')
                if len(tokens) >= 5:
                    content = " ".join(tokens[4:])
                    parsed.append({"Timestamp": " ".join(tokens[0:3]), "Raw_Content": content, "Event_Template": mask_text(content)})
        df = pd.DataFrame(parsed)
        df.to_csv(os.path.join("processed_logs", "linux_parsed.csv"), index=False)
        print(f"[?] Tokenized {len(df)} Linux lines. Unique structural templates: {df['Event_Template'].nunique()}")

    if os.path.exists(openstack_raw):
        parsed = []
        with open(openstack_raw, 'r', encoding='utf-8') as f:
            for line in f:
                tokens = line.strip().split(' ')
                if len(tokens) >= 4:
                    content = " ".join(tokens[3:])
                    parsed.append({"Timestamp": " ".join(tokens[0:2]), "Raw_Content": content, "Event_Template": mask_text(content)})
        df = pd.DataFrame(parsed)
        df.to_csv(os.path.join("processed_logs", "openstack_parsed.csv"), index=False)
        print(f"[?] Tokenized {len(df)} OpenStack lines. Unique structural templates: {df['Event_Template'].nunique()}")

    print("\n=== SYSTEM ARCHITECTURE INITIALIZED FLAWLESSLY ===")

if __name__ == "__main__":
    initialize_project()

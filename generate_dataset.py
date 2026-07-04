"""
Step 1 (v2) -- Dataset generation for BERT Security Log Classifier.

v2 fixes the v1 problem: v1 used disjoint vocabulary/prefixes per class
(INFO/WARN/ALERT, non-overlapping keywords) which let the model hit 100%
accuracy by memorizing surface patterns instead of learning anything.

v2 changes:
  - Shared vocabulary across classes (failed logins, unusual times, file
    access etc. appear in ALL three classes with different severity/context)
  - Ambiguous borderline examples deliberately mixed in
  - ~5% label noise (mislabeled rows), which is realistic for hand-labeled
    security data and prevents the model from overfitting to a clean signal
  - No consistent severity prefix (INFO/WARN/ALERT) as a giveaway shortcut

Run:
    python generate_dataset.py
Output:
    data/security_logs.csv
"""

import csv
import random

random.seed(42)

USERS = ["admin", "jsmith", "svc_backup", "root", "guest", "dbadmin", "webapp",
          "mchen", "svc_monitor", "operator", "deploy_bot", "analyst01"]
IPS_INTERNAL = [f"10.0.{random.randint(0,20)}.{random.randint(2,254)}" for _ in range(60)]
IPS_EXTERNAL = [f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(120)]
HOSTS = ["web-prod-01", "db-prod-02", "auth-svc", "api-gateway", "vpn-gw01",
         "file-server-03", "app-node-07", "mail-relay", "dns-primary", "backup-host"]
PORTS_COMMON = [22, 80, 443, 3389, 3306, 5432, 8080, 445]
PORTS_UNUSUAL = [4444, 1337, 6667, 31337, 9001, 2222, 8888, 6666]
SEVERITY_TAGS = ["INFO", "WARN", "ALERT", "NOTICE", "DEBUG"]  # no longer 1:1 with class

def ts():
    return f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

def tag():
    # severity tag is now randomized noise, not a reliable label shortcut
    return random.choice(SEVERITY_TAGS)

def normal_log():
    templates = [
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=login status=success src_ip={random.choice(IPS_INTERNAL)} attempt=1",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} scheduled backup job completed duration={random.randint(30,600)}s",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=file_read path=/reports/q{random.randint(1,4)}.pdf status=success",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=login status=failed attempt=1 src_ip={random.choice(IPS_INTERNAL)} reason=typo",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=logout session_duration={random.randint(60,7200)}s",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} package update applied version={random.randint(1,9)}.{random.randint(0,20)}.{random.randint(0,9)} status=success",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=password_change status=success src_ip={random.choice(IPS_INTERNAL)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} connection established src={random.choice(IPS_INTERNAL)} dst_port={random.choice(PORTS_COMMON)} protocol=TCP",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=sudo command=systemctl_restart status=success",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} logged in from usual location src_ip={random.choice(IPS_INTERNAL)} hour={random.randint(8,19)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=file_upload path=/shared/docs status=success size={random.randint(10,400)}KB",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} vpn session started user={random.choice(USERS)} src_ip={random.choice(IPS_INTERNAL)} duration={random.randint(30,480)}m",
    ]
    return random.choice(templates)()

def suspicious_log():
    templates = [
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=login status=failed attempt={random.randint(2,4)} src_ip={random.choice(IPS_EXTERNAL)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} unusual login time user={random.choice(USERS)} hour={random.choice([1,2,3,4,23])} src_ip={random.choice(IPS_INTERNAL)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=sudo command=view_passwd_file status=denied",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} port scan pattern src_ip={random.choice(IPS_EXTERNAL)} ports_probed={random.randint(3,10)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=file_access path=/etc/shadow status=denied src_ip={random.choice(IPS_INTERNAL)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} repeated password reset requests user={random.choice(USERS)} count={random.randint(3,6)} window=10m",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} login from new geolocation user={random.choice(USERS)} src_ip={random.choice(IPS_EXTERNAL)} status=success",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} larger than usual outbound transfer user={random.choice(USERS)} size={random.randint(400,1200)}MB dst_ip={random.choice(IPS_EXTERNAL)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} multiple failed sudo attempts user={random.choice(USERS)} count={random.randint(2,5)}",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} connection src={random.choice(IPS_EXTERNAL)} dst_port={random.choice(PORTS_UNUSUAL)} flagged=uncommon_port status=allowed",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=login status=success src_ip={random.choice(IPS_EXTERNAL)} attempt=3 note=eventually_succeeded",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=file_upload path=/shared/docs status=success size={random.randint(400,900)}KB src_ip={random.choice(IPS_EXTERNAL)}",
    ]
    return random.choice(templates)()

def malicious_log():
    templates = [
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} brute force detected user={random.choice(USERS)} attempts={random.randint(20,200)} src_ip={random.choice(IPS_EXTERNAL)} action=blocked",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} SQL injection payload in request param='id' src_ip={random.choice(IPS_EXTERNAL)} action=blocked",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} ransomware signature matched files_changed={random.randint(50,5000)} host_isolated=true",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} privilege escalation succeeded user={random.choice(USERS)} from=user to=root method=exploit action=session_terminated",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} known C2 beacon src={random.choice(IPS_EXTERNAL)} dst_port={random.choice(PORTS_UNUSUAL)} action=blocked",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} malware signature detected file=/tmp/{random.choice(['x','svc','update','tmp'])}{random.randint(100,999)}.exe action=quarantined",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} data exfiltration confirmed size={random.randint(1000,20000)}MB dst_ip={random.choice(IPS_EXTERNAL)} action=connection_terminated",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} DDoS traffic pattern requests_per_sec={random.randint(5000,50000)} src_ips={random.randint(100,5000)} action=mitigated",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} unauthorized admin account created user=backdoor_{random.randint(100,999)} src_ip={random.choice(IPS_EXTERNAL)} action=account_disabled",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} credential dump detected file=/tmp/hashes.txt user={random.choice(USERS)} action=incident_created",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=login status=failed attempt={random.randint(50,300)} src_ip={random.choice(IPS_EXTERNAL)} action_taken=ip_banned",
        lambda: f"[{ts()}] {tag()} {random.choice(HOSTS)} user={random.choice(USERS)} action=sudo command=disable_firewall status=success src_ip={random.choice(IPS_EXTERNAL)}",
    ]
    return random.choice(templates)()

def build(n_per_class=1200, noise_rate=0.05):
    rows = []
    generators = {0: normal_log, 1: suspicious_log, 2: malicious_log}
    for true_label, gen in generators.items():
        for _ in range(n_per_class):
            text = gen()
            if random.random() < noise_rate:
                # inject label noise: assign a wrong label to simulate
                # real-world annotation error / genuinely ambiguous cases
                wrong_choices = [l for l in (0, 1, 2) if l != true_label]
                label = random.choice(wrong_choices)
            else:
                label = true_label
            rows.append((text, label))
    random.shuffle(rows)
    return rows

if __name__ == "__main__":
    rows = build(n_per_class=1200, noise_rate=0.05)
    with open("data/security_logs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to data/security_logs.csv")
    print("Label counts:", {i: sum(1 for _, l in rows if l == i) for i in range(3)})
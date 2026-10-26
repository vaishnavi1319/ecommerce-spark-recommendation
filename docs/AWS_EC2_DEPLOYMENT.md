# AWS EC2 & S3 Deployment Guide
## Project: E-Commerce Product Recommendation Using Apache Spark

This guide provides step-by-step instructions for deploying and running the **SparkRec** Big Data e-commerce recommendation system on Amazon Web Services (AWS) using **EC2** (compute) and **S3** (object storage).

---

## 1. Cloud Architecture Overview

```
                                  ┌────────────────────────┐
                                  │      Client Web        │
                                  │   (Browser / Mobile)   │
                                  └───────────┬────────────┘
                                              │ HTTP (Port 80)
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ AWS EC2 Instance (Ubuntu 22.04 LTS / t3.large)                              │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Nginx Reverse Proxy (Port 80 -> 127.0.0.1:5000)                     │   │
│   │   • Gzip compression, SSL termination, request buffering            │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Flask REST API Backend + PySpark Application (sparkrec.service)     │   │
│   │   • Authentication (JWT & bcrypt)                                   │   │
│   │   • Product Catalogue & User Interaction Tracking                   │   │
│   │   • Real-Time Recommendation Serving (Sub-10ms JSON cache)          │   │
│   │   • Distributed ALS Model Training Pipeline                         │   │
│   └───────────────┬──────────────────────────────────┬──────────────────┘   │
│                   │                                  │                      │
│                   ▼                                  ▼                      │
│   ┌───────────────────────────────┐  ┌──────────────────────────────────┐   │
│   │ Local MongoDB 7.0 Community   │  │ Apache Spark 3.5 Engine (Local)  │   │
│   │   • Users & Roles             │  │   • Data Loading & Clean-up      │   │
│   │   • Product catalogue         │  │   • DataFrame SQL Aggregations   │   │
│   │   • Live user interactions    │  │   • MLlib ALS Model Training     │   │
│   └───────────────────────────────┘  └────────────────┬─────────────────┘   │
└───────────────────────────────────────────────────────┼─────────────────────┘
                                                        │
                                                        │ S3 API (Boto3 / s3a)
                                                        ▼
                                       ┌──────────────────────────────────┐
                                       │ AWS Amazon S3 Bucket             │
                                       │   s3://ecommerce-spark-dataset/  │
                                       │   ├── raw/                       │
                                       │   │   └── interactions.csv       │
                                       │   └── processed/                 │
                                       │       ├── recommendations.json   │
                                       │       └── analytics.json         │
                                       └──────────────────────────────────┘
```

---

## 2. Prerequisites

1. An active AWS Account ([aws.amazon.com](https://aws.amazon.com)).
2. An SSH Key Pair (`.pem` file) created in your target AWS region (e.g. `us-east-1` or `ap-south-1`).
3. Basic knowledge of terminal commands.

---

## 3. Step 1: Provisioning the AWS EC2 Instance

### Recommended Specifications
| Property | Recommendation | Reason |
|---|---|---|
| **AMI** | Ubuntu Server 22.04 LTS (HVM), SSD Volume Type | High stability, Debian packages for OpenJDK & MongoDB |
| **Architecture** | 64-bit (x86) | Maximum PySpark and JVM binary compatibility |
| **Instance Type** | `t3.large` (2 vCPUs, 8 GB RAM) or `t3.xlarge` (4 vCPUs, 16 GB RAM) | Spark ALS matrix factorization is memory-intensive |
| **Storage** | 30 GB gp3 (General Purpose SSD) | Accommodates OS, Spark binaries, and raw datasets |

### Security Group Inbound Rules
Configure your EC2 Security Group with the following inbound rules:

| Type | Protocol | Port Range | Source | Description |
|---|---|---|---|---|
| SSH | TCP | 22 | Your IP / `0.0.0.0/0` | Secure Shell administration |
| HTTP | TCP | 80 | `0.0.0.0/0` | Public Web access via Nginx |
| HTTPS | TCP | 443 | `0.0.0.0/0` | Secure SSL access (Optional) |
| Custom TCP | TCP | 5000 | `0.0.0.0/0` | Direct Flask API testing (Optional) |

---

## 4. Step 2: S3 Bucket & IAM Role Setup

### Create S3 Bucket
1. Open the [AWS S3 Console](https://s3.console.aws.amazon.com/s3/).
2. Click **Create bucket**.
3. Name your bucket (e.g., `ecommerce-spark-dataset-yourname`).
4. Select the region matching your EC2 instance (e.g., `us-east-1`).
5. Keep default encryption and block public access settings enabled.
6. Click **Create bucket**.

### Configure IAM Role for EC2 (Best Practice)
Instead of embedding AWS secret keys inside the code or `.env`, attach an IAM Role to your EC2 instance:
1. Open the [AWS IAM Console](https://console.aws.amazon.com/iam/).
2. Click **Roles** → **Create role**.
3. Select **AWS service** → **EC2**.
4. Attach the managed policy: `AmazonS3FullAccess` (or create a custom policy restricting access to your bucket).
5. Name the role: `EC2-SparkRec-S3-Role`.
6. Attach this role to your EC2 instance:
   * EC2 Console → Instances → Select Instance → **Actions** → **Security** → **Modify IAM role** → Select `EC2-SparkRec-S3-Role` → **Update IAM role**.

*(Note: If using IAM Role, leave `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` empty in `.env`. Boto3 automatically discovers the instance profile credentials.)*

---

## 5. Step 3: Connecting & Running Automated Setup

### 1. SSH into the Instance
```bash
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@<EC2_PUBLIC_IPv4_DNS_OR_IP>
```

### 2. Upload / Clone the Project Repository
```bash
# Option A: Git clone
git clone <your-repo-url> bda-project
cd bda-project

# Option B: SCP upload from your local machine
# Run from local terminal:
# scp -i your-key.pem -r "a:/bda project" ubuntu@<EC2_IP>:/home/ubuntu/bda-project
```

### 3. Run the Automated Provisioning Script
The provided script installs OpenJDK 17, MongoDB 7.0, Nginx, Python virtual environment, dependencies, systemd service, and firewall rules:
```bash
cd /home/ubuntu/bda-project
chmod +x scripts/setup_ec2.sh scripts/deploy_ec2.sh
bash scripts/setup_ec2.sh
```

---

## 6. Step 4: Configuring Environment Variables (`.env`)

Edit `/home/ubuntu/bda-project/.env`:
```bash
nano /home/ubuntu/bda-project/.env
```

Ensure the following cloud parameters are set:
```ini
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0

# Database
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=ecommerce_spark

# AWS Cloud Settings
AWS_REGION=us-east-1
S3_BUCKET_NAME=ecommerce-spark-dataset-yourname

# (Optional: Only if IAM Role is NOT used)
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...

# Spark Memory Settings (tuned for EC2 t3.large)
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=3g
SPARK_EXECUTOR_MEMORY=3g
```

Restart the service after editing:
```bash
sudo systemctl restart sparkrec.service
```

---

## 7. Step 5: Running Spark Pipeline & Syncing with S3

### A. Run Spark ALS Pipeline on EC2
You can trigger the pipeline directly from the Admin Web UI (`http://<EC2-IP>/admin.html`) or via the command line:

```bash
source venv/bin/activate
python3 spark/train_model.py --large --rank 12 --max-iter 15
```

### B. Upload Dataset & Results to S3
You can upload data to S3 via the Admin Web UI Cloud Panel or using Python:
```python
from backend.services.cloud_service import upload_dataset_to_s3, upload_results_to_s3
upload_dataset_to_s3()
upload_results_to_s3()
```

---

## 8. Step 6: Verifying Health & Services

Verify everything is running smoothly:
```bash
# 1. Check Flask systemd service
sudo systemctl status sparkrec.service

# 2. Check MongoDB status
sudo systemctl status mongod

# 3. Check Nginx reverse proxy
sudo systemctl status nginx

# 4. Test API health endpoint via Nginx (port 80)
curl http://localhost/api/health

# 5. Test Public Spark Analytics endpoint
curl http://localhost/api/analytics/public
```

Access the application in your browser:
* **Web Storefront:** `http://<EC2-PUBLIC-IP>/`
* **Product Catalogue:** `http://<EC2-PUBLIC-IP>/products.html`
* **Personalized Recs:** `http://<EC2-PUBLIC-IP>/recommendations.html`
* **Spark Analytics Dashboard:** `http://<EC2-PUBLIC-IP>/dashboard.html`
* **Admin & Cloud Console:** `http://<EC2-PUBLIC-IP>/admin.html`

---

## 9. Troubleshooting & Operations

| Issue | Cause | Solution |
|---|---|---|
| **502 Bad Gateway** | Flask/Gunicorn service is down | Run `sudo journalctl -u sparkrec.service -n 50` to inspect error |
| **Spark Out of Memory (OOM)** | Driver memory exceeds EC2 RAM | Lower `SPARK_DRIVER_MEMORY` to `2g` in `.env` |
| **S3 Access Denied** | Missing IAM policy or credentials | Ensure IAM Role attached to EC2 has `s3:PutObject`, `s3:GetObject` permissions |
| **MongoDB connection refused** | MongoDB daemon not started | Run `sudo systemctl restart mongod` |

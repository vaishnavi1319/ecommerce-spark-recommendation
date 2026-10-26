# E-Commerce Product Recommendation Using Spark
### Big Data Analytics (Apache Spark MLlib) & Cloud Computing (AWS S3 + AWS EC2)

![Apache Spark](https://img.shields.io/badge/Apache_Spark-3.5.1-E25A1C?logo=apachespark&logoColor=white)
![AWS S3](https://img.shields.io/badge/AWS_S3-Storage-569A31?logo=amazons3&logoColor=white)
![AWS EC2](https://img.shields.io/badge/AWS_EC2-Compute-FF9900?logo=amazonec2&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0%2B-47A248?logo=mongodb&logoColor=white)

---

## 📖 Project Overview

**SparkRec** is an enterprise-grade Big Data e-commerce product recommendation platform designed to demonstrate distributed data processing and cloud architecture. 

The system leverages **Apache Spark (PySpark)** and **Spark MLlib** to clean, transform, and analyze large-scale e-commerce interaction datasets (up to 1M+ interactions) and train a collaborative filtering recommendation model using the **Alternating Least Squares (ALS)** algorithm. The entire architecture is integrated with **Amazon Web Services (AWS)** using **Amazon S3** for persistent dataset/model artifact storage and **Amazon EC2** with Nginx and Systemd for high-availability cloud deployment.

---

## ⚡ Mandatory Technologies & Architecture

### 1. Big Data Analytics: Apache Spark (Spark MLlib)
* **Distributed Data Processing:** PySpark DataFrames for cleaning, type-casting, duplicate removal, and partition-aware schema parsing.
* **Spark SQL Aggregations:** Distributed aggregations computing interaction metrics, category distribution, top-rated items, monthly purchase trends, and user activity funnels.
* **Spark MLlib ALS Algorithm:** Collaborative filtering matrix factorization using implicit/explicit feedback, with hyperparameters for latent factors (`rank`), iterations (`maxIter`), and regularization (`regParam`).
* **Cold-Start Fallback:** Intelligent fallback to trending and category-based popularity caches for new users with zero prior interactions.

### 2. Cloud Computing: AWS S3 + AWS EC2
* **Amazon S3 Storage:** Datasets and trained model artifacts (`recommendations.json`, `analytics.json`, `model_stats.json`) are stored and retrieved from S3 buckets via Boto3, complete with presigned download URL generation.
* **Amazon EC2 Compute:** Complete deployment automation with automated provisioning scripts (`scripts/setup_ec2.sh`), production systemd unit (`sparkrec.service`), and Nginx reverse proxy configuration (`scripts/nginx_sparkrec.conf`).
* **AWS EMR Support (Distributed Spark):** Native support for launching multi-node Amazon EMR clusters and submitting distributed Spark steps.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ AWS EC2 Instance (Ubuntu 22.04 LTS / t3.large)                              │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Nginx Web Server / Reverse Proxy (Port 80)                          │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │ proxy_pass http://127.0.0.1:5000     │
│                                      ▼                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Flask REST API Backend (sparkrec.service)                           │   │
│   │   • JWT Auth & Role-based Access Control (Admin / Customer)         │   │
│   │   • Sub-10ms Recommendation Serving Cache                           │   │
│   │   • Thread-safe Spark Pipeline Execution Controller                 │   │
│   └───────────────┬──────────────────────────────────┬──────────────────┘   │
│                   │                                  │                      │
│                   ▼                                  ▼                      │
│   ┌───────────────────────────────┐  ┌──────────────────────────────────┐   │
│   │ MongoDB Community / Atlas     │  │ Apache Spark 3.5 MLlib Engine    │   │
│   │   • Users, Products, Logs     │  │   • Data Cleaning & Preprocess   │   │
│   │   • Live user interactions    │  │   • ALS Collaborative Filtering  │   │
│   └───────────────────────────────┘  └────────────────┬─────────────────┘   │
└───────────────────────────────────────────────────────┼─────────────────────┘
                                                        │ Boto3 S3 Sync
                                                        ▼
                                       ┌──────────────────────────────────┐
                                       │ Amazon S3 Bucket                 │
                                       │   s3://ecommerce-spark-dataset/  │
                                       └──────────────────────────────────┘
```

---

## 🗂️ Project Directory Structure

```
a:/bda project/
├── .env.example                     # Environment template with Spark & AWS settings
├── requirements.txt                 # Python dependencies (PySpark, Flask, Boto3, PyMongo)
├── README.md                        # Primary project documentation
├── backend/                         # Flask REST API Backend
│   ├── app.py                       # App factory, static serving & error handlers
│   ├── models/
│   │   └── db_models.py             # MongoDB schema & PyMongo collections
│   ├── routes/
│   │   ├── auth_routes.py           # Registration, login, profile (/api/auth)
│   │   ├── product_routes.py        # Catalogue, search, pagination (/api/products)
│   │   ├── interaction_routes.py    # Log views, carts, ratings (/api/interactions)
│   │   ├── recommendation_routes.py # Personalized & category recs (/api/recommendations)
│   │   ├── admin_routes.py          # Pipeline triggers & analytics (/api/admin)
│   │   └── cloud_routes.py          # AWS S3 & EMR cloud operations (/api/cloud)
│   └── services/
│       ├── spark_service.py         # Thread-safe Spark training orchestration
│       ├── recommendation_service.py# In-memory recommendation serving & cold-start
│       └── cloud_service.py         # Boto3 integration for S3 & EMR with local fallback
├── data/
│   ├── raw/                         # Raw interaction and product CSV files
│   └── processed/                   # Spark MLlib outputs (recommendations.json, ALS model)
├── docs/
│   └── AWS_EC2_DEPLOYMENT.md        # Comprehensive EC2 and S3 deployment guide
├── frontend/                        # Responsive Web Application (HTML5, CSS3, JS)
│   ├── index.html                   # Storefront landing page & featured items
│   ├── products.html                # Product catalogue with live search & filters
│   ├── recommendations.html         # "For You" Spark ALS personalized feed
│   ├── dashboard.html               # Real-time Apache Spark analytics dashboard
│   ├── admin.html                   # Admin console: Spark training & AWS Cloud panel
│   ├── login.html                   # JWT authentication portal
│   ├── css/
│   │   └── style.css                # Custom modern design system
│   └── js/
│       ├── api.js                   # Unified API fetch client
│       └── ui.js                    # UI notifications, modals, and formatters
├── scripts/                         # Automation & Deployment Utilities
│   ├── generate_large_dataset.py    # E-commerce dataset generator (10K to 1M+ rows)
│   ├── run_local.py                 # Cross-platform local startup script
│   ├── setup_ec2.sh                 # One-click Ubuntu EC2 provisioning script
│   ├── deploy_ec2.sh                # Fast continuous deployment script for EC2
│   ├── sparkrec.service             # Systemd production unit file
│   └── nginx_sparkrec.conf          # Nginx reverse proxy configuration
└── spark/                           # Apache Spark & MLlib Processing Core
    ├── spark_session.py             # SparkSession builder with memory & S3 tuning
    ├── data_loader.py               # DataFrame loader with explicit schema definition
    ├── preprocessing.py             # Data transformation & interaction matrix builder
    ├── analytics.py                 # Spark SQL aggregations & metrics engine
    ├── recommendation_model.py      # Spark MLlib ALS model training & evaluation
    └── train_model.py               # Complete CLI & background training pipeline
```

---

## 🚀 Local Quickstart Guide

### 1. Prerequisites
- **Python:** 3.10, 3.11, 3.12, or 3.13
- **Java:** OpenJDK 11, 17, or 19 (required by Apache Spark)
- **MongoDB:** Local MongoDB Community Edition or free MongoDB Atlas cluster

### 2. Installation
```bash
# Clone the repository and navigate into it
cd "a:/bda project"

# Create and activate Python virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure `JAVA_HOME` points to your Java installation (e.g. `C:\Program Files\Java\jdk-19` or `/usr/lib/jvm/java-17-openjdk-amd64`).

### 4. Run Apache Spark Pipeline (CLI)
You can run the complete Spark data preprocessing, analytics, and ALS MLlib training pipeline directly:
```bash
python spark/train_model.py --rank 10 --max-iter 10
```
This loads `data/raw/ecommerce_interactions.csv`, runs Spark SQL analytics, trains the ALS collaborative filtering model, and generates recommendations for users saved into `data/processed/`.

### 5. Launch the Web Application
Run the local launcher:
```bash
python scripts/run_local.py
```
Or start via Flask directly:
```bash
python -m backend.app
```
Open your browser and navigate to:
* **Storefront:** [http://localhost:5000](http://localhost:5000)
* **Products:** [http://localhost:5000/products.html](http://localhost:5000/products.html)
* **For You (Recommendations):** [http://localhost:5000/recommendations.html](http://localhost:5000/recommendations.html)
* **Spark Analytics Dashboard:** [http://localhost:5000/dashboard.html](http://localhost:5000/dashboard.html)
* **Admin Control Panel:** [http://localhost:5000/admin.html](http://localhost:5000/admin.html)

---

## ☁️ AWS Cloud Deployment (EC2 + S3)

Detailed instructions are available in [docs/AWS_EC2_DEPLOYMENT.md](docs/AWS_EC2_DEPLOYMENT.md).

### Quick Summary for EC2:
1. **Launch EC2 Instance:** Ubuntu 22.04 LTS, `t3.large` (2 vCPUs, 8 GB RAM), 30 GB gp3 SSD.
2. **Security Group:** Inbound ports `22` (SSH), `80` (HTTP), `443` (HTTPS), `5000` (Flask optional).
3. **IAM Role:** Attach role with `AmazonS3FullAccess` to the EC2 instance.
4. **Deploy:**
   ```bash
   ssh -i your-key.pem ubuntu@<EC2-IP>
   git clone <repo> bda-project
   cd bda-project
   bash scripts/setup_ec2.sh
   ```
5. **Verify:**
   ```bash
   curl http://localhost/api/health
   curl http://localhost/api/analytics/public
   ```

---

## 🔑 Default Credentials
Admin password: Configure securely using environment variables.
Do not use default credentials in production.

---

## 📡 REST API Reference

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/health` | Public | System health and Spark status |
| `GET` | `/api/products` | Public | Search and browse product catalogue |
| `GET` | `/api/popular-products` | Public | Cold-start popular products from Spark analytics |
| `GET` | `/api/recommendations/<user_id>` | User/Public | Get top-N personalized recommendations for a user |
| `GET` | `/api/recommendations/me` | Logged In | Get recommendations for current authenticated user |
| `POST` | `/api/interactions` | Logged In | Log user interaction (view, cart, purchase, rating) |
| `GET` | `/api/analytics/public` | Public | Apache Spark DataFrame analytics metrics for dashboard |
| `POST` | `/api/train-model` | Admin | Trigger background PySpark MLlib ALS training |
| `GET` | `/api/model-status` | Logged In | Check live training progress and ALS evaluation metrics |
| `GET` | `/api/cloud/status` | Logged In | AWS S3 connectivity check |
| `POST` | `/api/cloud/upload-dataset` | Admin | Upload local CSV dataset to Amazon S3 |
| `POST` | `/api/cloud/upload-results` | Admin | Sync trained recommendation JSON artifacts to Amazon S3 |
| `GET` | `/api/cloud/s3/objects` | Admin | List dataset files and model artifacts in S3 bucket |

---

## ✅ Completed & Verified Implementation
## Project Implementation Status

The project includes Apache Spark MLlib-based recommendation
features and AWS cloud integration. Individual features must
be tested in the target environment before deployment.

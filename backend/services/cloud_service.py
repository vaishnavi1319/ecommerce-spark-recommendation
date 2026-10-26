"""
=============================================================
Cloud Service — AWS S3 & EMR Integration
=============================================================
Provides cloud computing capabilities:
  • Amazon S3  — dataset upload / download / presigned URLs
  • Amazon EMR — cluster launch, Spark job submission, status

FALLBACK DESIGN:
  If AWS credentials are absent or invalid, every function
  returns a sensible error dict so the rest of the app can
  still run in local mode without crashing.

Environment variables consumed:
  AWS_ACCESS_KEY_ID       — IAM access key
  AWS_SECRET_ACCESS_KEY   — IAM secret
  AWS_REGION              — default: us-east-1
  S3_BUCKET_NAME          — target bucket name
  EMR_LOG_URI             — s3://<bucket>/emr-logs/
  EMR_EC2_KEY_PAIR        — (optional) key pair for SSH
=============================================================
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Config from environment ───────────────────────────────
AWS_KEY    = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET  = os.getenv("S3_BUCKET_NAME", "ecommerce-spark-dataset")
EMR_LOG_URI     = os.getenv("EMR_LOG_URI", f"s3://{S3_BUCKET}/emr-logs/")
EMR_EC2_KEY     = os.getenv("EMR_EC2_KEY_PAIR", "")
EMR_SUBNET_ID   = os.getenv("EMR_SUBNET_ID", "")

# Local paths
DATASET_LOCAL    = os.getenv("DATASET_PATH", "data/raw/ecommerce_interactions.csv")
LARGE_LOCAL      = os.getenv("LARGE_DATASET_PATH", "data/raw/ecommerce_large.csv")
PROCESSED_PATH   = os.getenv("PROCESSED_DATA_PATH", "data/processed/")


# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────

def _has_credentials() -> bool:
    """Return True if AWS credentials look non-empty."""
    return bool(AWS_KEY and AWS_SECRET
                and "your-aws" not in AWS_KEY.lower()
                and "your-aws" not in AWS_SECRET.lower())


def _get_boto3():
    """Import boto3 and return (boto3, None) or (None, error_str)."""
    try:
        import boto3
        return boto3, None
    except ImportError:
        return None, "boto3 not installed — run: pip install boto3"


def _make_client(service: str):
    """Create a boto3 client or return (None, error_msg)."""
    if not _has_credentials():
        return None, "AWS credentials not configured in .env"
    boto3, err = _get_boto3()
    if err:
        return None, err
    try:
        client = boto3.client(
            service,
            region_name=AWS_REGION,
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
        )
        return client, None
    except Exception as e:
        return None, str(e)


# ──────────────────────────────────────────────────────────
# CLOUD STATUS
# ──────────────────────────────────────────────────────────

def get_cloud_status() -> dict:
    """
    Check AWS connectivity and return a status report.

    Returns:
        dict with keys: connected, region, bucket, s3_available,
        emr_available, credentials_configured, message
    """
    status = {
        "connected": False,
        "region": AWS_REGION,
        "bucket": S3_BUCKET,
        "s3_available": False,
        "emr_available": False,
        "credentials_configured": _has_credentials(),
        "local_fallback": True,
        "message": "",
        "checked_at": datetime.utcnow().isoformat(),
    }

    if not _has_credentials():
        status["message"] = (
            "AWS credentials not configured. Running in local mode. "
            "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env to enable cloud features."
        )
        return status

    # Test S3
    s3, err = _make_client("s3")
    if err:
        status["message"] = f"S3 error: {err}"
        return status

    try:
        s3.head_bucket(Bucket=S3_BUCKET)
        status["s3_available"] = True
        status["connected"] = True
    except Exception as e:
        err_msg = str(e)
        if "404" in err_msg or "NoSuchBucket" in err_msg:
            # Bucket doesn't exist — credentials work but bucket needs creation
            status["connected"] = True
            status["s3_available"] = False
            status["message"] = f"S3 credentials valid. Bucket '{S3_BUCKET}' not found — create it first."
        else:
            status["message"] = f"S3 connection failed: {err_msg}"
            return status

    # Test EMR (just list clusters)
    emr, err = _make_client("emr")
    if not err:
        try:
            emr.list_clusters(ClusterStates=["RUNNING", "WAITING"])
            status["emr_available"] = True
        except Exception as e:
            status["emr_message"] = f"EMR check failed: {e}"

    if not status.get("message"):
        status["message"] = "AWS connected successfully."

    return status


# ──────────────────────────────────────────────────────────
# S3 OPERATIONS
# ──────────────────────────────────────────────────────────

def ensure_bucket_exists() -> dict:
    """Create the S3 bucket if it doesn't already exist."""
    s3, err = _make_client("s3")
    if err:
        return {"success": False, "error": err}
    try:
        if AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=S3_BUCKET)
        else:
            s3.create_bucket(
                Bucket=S3_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
            )
        return {"success": True, "bucket": S3_BUCKET, "message": "Bucket created"}
    except Exception as e:
        if "BucketAlreadyOwnedByYou" in str(e) or "BucketAlreadyExists" in str(e):
            return {"success": True, "bucket": S3_BUCKET, "message": "Bucket already exists"}
        return {"success": False, "error": str(e)}


def upload_dataset_to_s3(use_large: bool = False) -> dict:
    """
    Upload the local dataset CSV to S3.

    Args:
        use_large: If True, upload the large dataset

    Returns:
        dict with success, s3_path, size_mb, duration_seconds
    """
    local_path = LARGE_LOCAL if use_large else DATASET_LOCAL

    if not os.path.exists(local_path):
        return {
            "success": False,
            "error": f"Local dataset not found: {local_path}. "
                     "Run 'python scripts/generate_large_dataset.py' first.",
        }

    s3, err = _make_client("s3")
    if err:
        return {"success": False, "error": err}

    # Ensure bucket exists
    bucket_result = ensure_bucket_exists()
    if not bucket_result["success"]:
        return {"success": False, "error": bucket_result["error"]}

    file_name = os.path.basename(local_path)
    s3_key    = f"raw/{file_name}"
    s3_uri    = f"s3://{S3_BUCKET}/{s3_key}"

    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    start   = time.time()

    try:
        print(f"[CloudService] Uploading {local_path} → {s3_uri} ({size_mb:.1f} MB)...")
        s3.upload_file(local_path, S3_BUCKET, s3_key)
        elapsed = time.time() - start
        print(f"[CloudService] Upload complete in {elapsed:.1f}s")
        return {
            "success": True,
            "s3_path": s3_uri,
            "s3_key": s3_key,
            "bucket": S3_BUCKET,
            "size_mb": round(size_mb, 2),
            "duration_seconds": round(elapsed, 2),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def download_from_s3(s3_key: str, local_path: str) -> dict:
    """Download a file from S3 to local path."""
    s3, err = _make_client("s3")
    if err:
        return {"success": False, "error": err}

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        s3.download_file(S3_BUCKET, s3_key, local_path)
        return {"success": True, "local_path": local_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


def upload_results_to_s3() -> dict:
    """
    Upload the processed recommendations JSON back to S3 after training.
    This allows results to be shared / consumed by other services.
    """
    results = []
    for fname in ["recommendations.json", "analytics.json", "model_stats.json"]:
        local = PROCESSED_PATH + fname
        if not os.path.exists(local):
            continue
        s3, err = _make_client("s3")
        if err:
            return {"success": False, "error": err}
        try:
            s3_key = f"processed/{fname}"
            s3.upload_file(local, S3_BUCKET, s3_key)
            results.append({"file": fname, "s3_key": s3_key})
        except Exception as e:
            results.append({"file": fname, "error": str(e)})

    return {"success": True, "uploaded": results}


def get_presigned_url(s3_key: str, expiry_seconds: int = 3600) -> dict:
    """Generate a time-limited presigned download URL for an S3 object."""
    s3, err = _make_client("s3")
    if err:
        return {"success": False, "error": err}
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key},
            ExpiresIn=expiry_seconds,
        )
        return {"success": True, "url": url, "expires_in_seconds": expiry_seconds}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_s3_objects(prefix: str = "") -> dict:
    """List objects in the S3 bucket under a given prefix."""
    s3, err = _make_client("s3")
    if err:
        return {"success": False, "error": err, "objects": []}
    try:
        resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        objects = [
            {
                "key": o["Key"],
                "size_mb": round(o["Size"] / (1024 * 1024), 3),
                "last_modified": str(o["LastModified"]),
            }
            for o in resp.get("Contents", [])
        ]
        return {"success": True, "objects": objects, "count": len(objects)}
    except Exception as e:
        return {"success": False, "error": str(e), "objects": []}


# ──────────────────────────────────────────────────────────
# EMR OPERATIONS
# ──────────────────────────────────────────────────────────

def launch_emr_cluster(
    num_workers: int = 2,
    instance_type: str = "m5.xlarge",
    cluster_name: str = "SparkRec-EMR",
) -> dict:
    """
    Launch an AWS EMR cluster configured for PySpark workloads.

    Architecture:
      EC2 → EMR Master + Workers → S3 (data in/out)

    Args:
        num_workers    : Number of core (worker) nodes
        instance_type  : EC2 instance type for all nodes
        cluster_name   : Display name for the cluster

    Returns:
        dict with cluster_id, state, message
    """
    emr, err = _make_client("emr")
    if err:
        return {"success": False, "error": err}

    # Build configuration
    instances = {
        "MasterInstanceType": instance_type,
        "SlaveInstanceType":  instance_type,
        "InstanceCount":      num_workers + 1,  # +1 for master
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,
    }
    if EMR_SUBNET_ID:
        instances["Ec2SubnetId"] = EMR_SUBNET_ID
    if EMR_EC2_KEY:
        instances["Ec2KeyName"] = EMR_EC2_KEY

    try:
        response = emr.run_job_flow(
            Name=cluster_name,
            LogUri=EMR_LOG_URI,
            ReleaseLabel="emr-6.15.0",
            Applications=[
                {"Name": "Spark"},
                {"Name": "Hadoop"},
            ],
            Instances=instances,
            ServiceRole="EMR_DefaultRole",
            JobFlowRole="EMR_EC2_DefaultRole",
            VisibleToAllUsers=True,
            Tags=[
                {"Key": "Project", "Value": "SparkRec-BDA"},
                {"Key": "Environment", "Value": "Production"},
            ],
            Configurations=[
                {
                    "Classification": "spark-defaults",
                    "Properties": {
                        "spark.driver.memory":   "4g",
                        "spark.executor.memory": "4g",
                        "spark.sql.shuffle.partitions": "50",
                        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    },
                }
            ],
        )
        cluster_id = response["JobFlowId"]
        print(f"[EMR] Cluster launched: {cluster_id}")
        return {
            "success": True,
            "cluster_id": cluster_id,
            "state": "STARTING",
            "message": f"EMR cluster '{cluster_name}' starting. ID: {cluster_id}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def submit_spark_job(cluster_id: str, use_large: bool = False) -> dict:
    """
    Submit the Spark training job as an EMR Step.

    The train_model.py script must first be uploaded to S3.

    Args:
        cluster_id: EMR cluster ID (e.g. j-XXXXXXXXXXXX)
        use_large : Use the large S3 dataset

    Returns:
        dict with step_id, state, message
    """
    emr, err = _make_client("emr")
    if err:
        return {"success": False, "error": err}

    dataset_flag = "--large" if use_large else ""
    script_s3 = f"s3://{S3_BUCKET}/scripts/train_model.py"

    try:
        response = emr.add_job_flow_steps(
            JobFlowId=cluster_id,
            Steps=[
                {
                    "Name": "SparkRec-Training",
                    "ActionOnFailure": "CONTINUE",
                    "HadoopJarStep": {
                        "Jar": "command-runner.jar",
                        "Args": [
                            "spark-submit",
                            "--deploy-mode", "cluster",
                            "--master", "yarn",
                            "--conf", "spark.driver.memory=4g",
                            "--conf", "spark.executor.memory=4g",
                            script_s3,
                            "--s3",
                            dataset_flag,
                        ],
                    },
                }
            ],
        )
        step_id = response["StepIds"][0]
        print(f"[EMR] Step submitted: {step_id}")
        return {
            "success": True,
            "step_id": step_id,
            "cluster_id": cluster_id,
            "message": f"Spark training job submitted. Step ID: {step_id}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_emr_cluster_status(cluster_id: str) -> dict:
    """Return current status of an EMR cluster."""
    emr, err = _make_client("emr")
    if err:
        return {"success": False, "error": err}
    try:
        resp = emr.describe_cluster(ClusterId=cluster_id)
        cluster = resp["Cluster"]
        state   = cluster["Status"]["State"]
        return {
            "success": True,
            "cluster_id": cluster_id,
            "state": state,
            "name": cluster.get("Name"),
            "master_dns": cluster.get("MasterPublicDnsName", ""),
            "ready": state in ("RUNNING", "WAITING"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_emr_clusters() -> dict:
    """List active and recently terminated EMR clusters."""
    emr, err = _make_client("emr")
    if err:
        return {"success": False, "error": err, "clusters": []}
    try:
        resp = emr.list_clusters(
            ClusterStates=["STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING",
                           "TERMINATING", "TERMINATED", "TERMINATED_WITH_ERRORS"]
        )
        clusters = [
            {
                "id":    c["Id"],
                "name":  c["Name"],
                "state": c["Status"]["State"],
            }
            for c in resp.get("Clusters", [])
        ]
        return {"success": True, "clusters": clusters}
    except Exception as e:
        return {"success": False, "error": str(e), "clusters": []}


def terminate_emr_cluster(cluster_id: str) -> dict:
    """Terminate an EMR cluster to stop incurring costs."""
    emr, err = _make_client("emr")
    if err:
        return {"success": False, "error": err}
    try:
        emr.terminate_job_flows(JobFlowIds=[cluster_id])
        return {"success": True, "cluster_id": cluster_id, "message": "Cluster termination initiated"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ──────────────────────────────────────────────────────────
# UPLOAD TRAINING SCRIPT TO S3
# ──────────────────────────────────────────────────────────

def upload_training_script_to_s3() -> dict:
    """
    Upload spark/train_model.py to S3 so EMR can run it.
    Must be called before submit_spark_job().
    """
    script_path = "spark/train_model.py"
    if not os.path.exists(script_path):
        return {"success": False, "error": f"Script not found: {script_path}"}

    s3, err = _make_client("s3")
    if err:
        return {"success": False, "error": err}

    try:
        ensure_bucket_exists()
        s3.upload_file(script_path, S3_BUCKET, "scripts/train_model.py")
        return {
            "success": True,
            "s3_key": "scripts/train_model.py",
            "s3_uri": f"s3://{S3_BUCKET}/scripts/train_model.py",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

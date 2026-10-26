"""
=============================================================
Cloud Routes — AWS S3 & EMR API Endpoints
=============================================================
GET   /api/cloud/status          — AWS connectivity check
POST  /api/cloud/upload-dataset  — Upload local CSV → S3
POST  /api/cloud/upload-results  — Upload trained results → S3
POST  /api/cloud/emr/launch      — Launch EMR cluster
POST  /api/cloud/emr/submit      — Submit Spark job to EMR
GET   /api/cloud/emr/status/<id> — Cluster status
GET   /api/cloud/emr/clusters    — List clusters
POST  /api/cloud/emr/terminate   — Terminate a cluster
GET   /api/cloud/s3/objects      — List S3 objects
=============================================================
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.db_models import UserModel
from backend.services.cloud_service import (
    get_cloud_status,
    upload_dataset_to_s3,
    upload_results_to_s3,
    upload_training_script_to_s3,
    ensure_bucket_exists,
    list_s3_objects,
    get_presigned_url,
    launch_emr_cluster,
    submit_spark_job,
    get_emr_cluster_status,
    list_emr_clusters,
    terminate_emr_cluster,
)

cloud_bp = Blueprint("cloud", __name__)


def _require_admin():
    """Return (user, error_response) — error_response is None if admin OK."""
    try:
        uid  = int(get_jwt_identity())
        user = UserModel().find_by_id(uid)
        if not user or user.get("role") != "admin":
            return None, (jsonify({"error": "Admin access required"}), 403)
        return user, None
    except Exception as e:
        return None, (jsonify({"error": str(e)}), 401)


# ── Cloud Connectivity ────────────────────────────────────

@cloud_bp.route("/api/cloud/status", methods=["GET"])
@jwt_required(optional=True)
def cloud_status():
    """Check AWS connectivity — accessible to all logged-in users."""
    status = get_cloud_status()
    return jsonify(status), 200


# ── S3 Operations ─────────────────────────────────────────

@cloud_bp.route("/api/cloud/upload-dataset", methods=["POST"])
@jwt_required()
def upload_dataset():
    """Upload local dataset CSV to S3. Admin only."""
    _, err = _require_admin()
    if err:
        return err

    data      = request.get_json() or {}
    use_large = data.get("use_large", False)

    result = upload_dataset_to_s3(use_large=use_large)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@cloud_bp.route("/api/cloud/upload-results", methods=["POST"])
@jwt_required()
def upload_results():
    """Upload trained model results (JSONs) from local to S3. Admin only."""
    _, err = _require_admin()
    if err:
        return err

    result = upload_results_to_s3()
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@cloud_bp.route("/api/cloud/s3/objects", methods=["GET"])
@jwt_required()
def list_objects():
    """List objects in the S3 bucket."""
    _, err = _require_admin()
    if err:
        return err

    prefix = request.args.get("prefix", "")
    result = list_s3_objects(prefix=prefix)
    return jsonify(result), 200


@cloud_bp.route("/api/cloud/s3/presigned-url", methods=["GET"])
@jwt_required()
def presigned_url():
    """Get a presigned download URL for an S3 object."""
    _, err = _require_admin()
    if err:
        return err

    s3_key = request.args.get("key", "")
    if not s3_key:
        return jsonify({"error": "key parameter required"}), 400

    expiry = int(request.args.get("expiry", 3600))
    result = get_presigned_url(s3_key, expiry_seconds=expiry)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


# ── EMR Operations ────────────────────────────────────────

@cloud_bp.route("/api/cloud/emr/launch", methods=["POST"])
@jwt_required()
def emr_launch():
    """Launch a new EMR cluster. Admin only."""
    _, err = _require_admin()
    if err:
        return err

    data          = request.get_json() or {}
    num_workers   = int(data.get("num_workers", 2))
    instance_type = data.get("instance_type", "m5.xlarge")
    cluster_name  = data.get("cluster_name", "SparkRec-EMR")

    result = launch_emr_cluster(
        num_workers=num_workers,
        instance_type=instance_type,
        cluster_name=cluster_name,
    )
    status_code = 202 if result.get("success") else 400
    return jsonify(result), status_code


@cloud_bp.route("/api/cloud/emr/submit", methods=["POST"])
@jwt_required()
def emr_submit():
    """Submit Spark training job to an existing EMR cluster. Admin only."""
    _, err = _require_admin()
    if err:
        return err

    data       = request.get_json() or {}
    cluster_id = data.get("cluster_id", "")
    use_large  = data.get("use_large", False)

    if not cluster_id:
        return jsonify({"error": "cluster_id is required"}), 400

    # Upload training script to S3 first
    script_result = upload_training_script_to_s3()
    if not script_result.get("success"):
        return jsonify({
            "error": "Failed to upload training script to S3",
            "details": script_result.get("error"),
        }), 400

    result = submit_spark_job(cluster_id=cluster_id, use_large=use_large)
    status_code = 202 if result.get("success") else 400
    return jsonify(result), status_code


@cloud_bp.route("/api/cloud/emr/status/<string:cluster_id>", methods=["GET"])
@jwt_required()
def emr_status(cluster_id: str):
    """Get status of a specific EMR cluster."""
    _, err = _require_admin()
    if err:
        return err

    result = get_emr_cluster_status(cluster_id)
    return jsonify(result), 200


@cloud_bp.route("/api/cloud/emr/clusters", methods=["GET"])
@jwt_required()
def emr_clusters():
    """List all EMR clusters."""
    _, err = _require_admin()
    if err:
        return err

    result = list_emr_clusters()
    return jsonify(result), 200


@cloud_bp.route("/api/cloud/emr/terminate", methods=["POST"])
@jwt_required()
def emr_terminate():
    """Terminate an EMR cluster to stop costs. Admin only."""
    _, err = _require_admin()
    if err:
        return err

    data       = request.get_json() or {}
    cluster_id = data.get("cluster_id", "")
    if not cluster_id:
        return jsonify({"error": "cluster_id is required"}), 400

    result = terminate_emr_cluster(cluster_id)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@cloud_bp.route("/api/cloud/setup", methods=["POST"])
@jwt_required()
def cloud_setup():
    """One-step cloud setup: create bucket + upload dataset + upload script."""
    _, err = _require_admin()
    if err:
        return err

    data      = request.get_json() or {}
    use_large = data.get("use_large", False)

    steps = {}

    # 1. Ensure bucket
    bucket_result = ensure_bucket_exists()
    steps["bucket"] = bucket_result

    if not bucket_result.get("success"):
        return jsonify({"success": False, "steps": steps, "error": bucket_result.get("error")}), 400

    # 2. Upload dataset
    upload_result = upload_dataset_to_s3(use_large=use_large)
    steps["dataset_upload"] = upload_result

    # 3. Upload training script
    script_result = upload_training_script_to_s3()
    steps["script_upload"] = script_result

    all_ok = all([
        bucket_result.get("success"),
        upload_result.get("success"),
        script_result.get("success"),
    ])

    return jsonify({
        "success": all_ok,
        "steps": steps,
        "message": "Cloud setup complete." if all_ok else "Some steps failed.",
    }), 200 if all_ok else 207

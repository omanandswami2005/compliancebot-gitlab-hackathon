# Terraform config for GCS compliance evidence bucket
resource "google_storage_bucket" "compliance_evidence" {
  name     = "compliance-evidence-${var.project_id}"
  location = "US"

  retention_policy {
    retention_period = 31536000  # 1 year (SOC 2 requirement)
  }

  versioning {
    enabled = true  # Immutable evidence trail
  }

  lifecycle_rule {
    action { type = "SetStorageClass" storage_class = "NEARLINE" }
    condition { age = 90 }  # Move to cheaper storage after 90 days
  }
}

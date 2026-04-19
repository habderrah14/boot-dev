# Mini-project — 06-security

_Companion chapter:_ [`06-security.md`](../06-security.md)

**Goal.** Audit and harden an S3 bucket. Document your findings as a checklist.

**Acceptance criteria:**

- Block Public Access enabled at account and bucket level.
- HTTPS-only bucket policy applied.
- Versioning enabled.
- IAM policy for the app follows least privilege (specific actions, scoped resource ARNs).
- Access logging enabled (logs go to a separate bucket).
- No long-lived access keys — application uses an IAM role.
- Document each finding and remediation step in a markdown file.

**Hints:**

- `aws s3api get-public-access-block --bucket X` checks BPA status.
- `aws s3api get-bucket-policy --bucket X` shows the current policy.
- `aws s3api get-bucket-versioning --bucket X` checks versioning.

**Stretch:** Add a CloudFormation or Terraform template that creates a hardened bucket with all of the above configured from the start.

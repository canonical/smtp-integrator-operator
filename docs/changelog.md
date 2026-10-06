# Changelog

## Unreleased

### Terraform module

- Migrated the `terraform/` module to the [CC008 Charm Terraform
  Standards](https://github.com/canonical/operator-workflows/tree/main/terraform-compliance):
  - Renamed `versions.tf` to `terraform.tf`.
  - Added the mandatory `constraints` input variable.
  - Removed the default value of `model_uuid`, which is now a required input.
  - **Breaking:** the `base` input variable now defaults to `null` (deploy the
    charm's default base) instead of `"ubuntu@22.04"`. Set `base =
    "ubuntu@22.04"` explicitly to keep the previous behaviour.
  - Replaced the combined `endpoints` output with the standard `provides`
    output, listing the `smtp` and `smtp-legacy` integration endpoints, and
    added the mandatory `application` output.
  - Added a `terraform/MAJOR_VERSION` file to track the module's release train.

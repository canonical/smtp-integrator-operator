# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.smtp_integrator.name
}

output "application" {
  description = "The deployed application object."
  value       = juju_application.smtp_integrator
}

output "provides" {
  description = "Map of the provided integration endpoints."
  value = {
    smtp = {
      kind     = "endpoint"
      name     = juju_application.smtp_integrator.name
      endpoint = "smtp"
    }
    smtp_legacy = {
      kind     = "endpoint"
      name     = juju_application.smtp_integrator.name
      endpoint = "smtp-legacy"
    }
  }
}

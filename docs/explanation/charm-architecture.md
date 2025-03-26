# Charm architecture

The SMTP Integrator charm fetches a centralized SMTP configuration and propagates it through a Juju integration.

The SMTP Integrator can be deployed in Kubernetes and machine models.
As a workloadless charm, the SMTP Integrator doesn't have any OCI images.

The charm provides a library to facilitate the development of charms that use the SMTP integration.

## Juju events

According to the [Juju SDK](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/): "an event is a data structure that encapsulates part of the execution context of a charm".

For this charm, the following events are observed:

1. [config-changed](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/#config-changed): Usually fired in response to a configuration change using the GUI or CLI. Action: validate the configuration and propagate the SMTP configuration through the relation.
2. [update-status](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/#update-status): Fired periodically. Action: propagate the SMTP configuration through the relation.
3. [smtp-relation-created](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/#endpoint-relation-created): Custom event for when a new SMTP relations joins. Action: write the SMTP details in the relation databag. The `smtp` integration will share a secret id across the relation the requirer will be able to access to retrieve the password.
4. [smtp-legacy-relation-created](https://canonical-juju.readthedocs-hosted.com/en/latest/user/reference/hook/#endpoint-relation-created): Custom event for when a new legacy SMTP relations joins. Action: write the SMTP details in the relation databag. The `smtp-legacy` integration will share the password across the relation.

## Charm code overview

The `src/charm.py` is the default entry point for a charm and has the SmtpIntegratorOperatorCharm Python class which inherits from CharmBase.

CharmBase is the base class from which all Charms are formed, defined by [Ops](https://ops.readthedocs.io/en/latest/) (Python framework for developing charms).

See more information in [Ops documentation](https://juju.is/docs/sdk/ops).

The `__init__` method guarantees that the charm observes all events relevant to its operation and handles them.


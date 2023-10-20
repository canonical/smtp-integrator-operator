# Charm architecture

The SMTP Integrator charm fetches centralizes SMTP configuration and propagates it through a Juju integration.

## Juju events

According to the [Juju SDK](https://juju.is/docs/sdk/event): "an event is a data structure that encapsulates part of the execution context of a charm".

For this charm, the following events are observed:

1. [config-changed](https://juju.is/docs/sdk/config-changed-event): usually fired in response to a configuration change using the GUI or CLI. Action: validate the configuration and propagate the SMTP configuration through the relation.
1. [update-status](https://juju.is/docs/sdk/update-status-event): fired periodically. Action: propagate the SMTP configuration through the relation.
3. [smtp-relation-joined](https://juju.is/docs/sdk/relation-name-relation-joined-event): Custom event for when a new SMTP relations joins. Action: write the SMTP details in the relation databag.
3. [smtp-legacy-relation-joined](https://juju.is/docs/sdk/relation-name-relation-joined-event): Custom event for when a new legacy SMTP relations joins. Action: write the SMTP details in the relation databag.

## Charm code overview

The `src/charm.py` is the default entry point for a charm and has the SmtpIntegratorOperatorCharm Python class which inherits from CharmBase.

CharmBase is the base class from which all Charms are formed, defined by [Ops](https://juju.is/docs/sdk/ops) (Python framework for developing charms).

See more information in [Charm](https://juju.is/docs/sdk/constructs#heading--charm).

The `__init__` method guarantees that the charm observes all events relevant to its operation and handles them.

[![CharmHub Badge](https://charmhub.io/smtp-integrator/badge.svg)](https://charmhub.io/smtp-integrator)
[![Publish to edge](https://github.com/canonical/smtp-integrator-operator/actions/workflows/publish_charm.yaml/badge.svg)](https://github.com/canonical/smtp-integrator-operator/actions/workflows/publish_charm.yaml)
[![Promote charm](https://github.com/canonical/smtp-integrator-operator/actions/workflows/promote_charm.yaml/badge.svg)](https://github.com/canonical/smtp-integrator-operator/actions/workflows/promote_charm.yaml)
[![Discourse Status](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.charmhub.io&style=flat&label=CharmHub%20Discourse)](https://discourse.charmhub.io)

# SMTP Integrator Operator

A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators)
deploying and managing a SMTP Integrator on Kubernetes and bare metal. SMTP
is an Internet standard communication protocol for email transmission.

This charm simplifies configuration of SMTP client by providing a single point
of configuration for all the requirers using the same SMTP server. It can be
deployed on many different Kubernetes platforms, from [MicroK8s](https://microk8s.io)
to [Charmed Kubernetes](https://ubuntu.com/kubernetes), public cloud Kubernetes
offerings and virtual machines or bare metal.

As such, the charm makes it easy to manage and propagate SMTP configuration, while
giving the freedom to deploy on the substrate of their choice.

For DevOps or SRE teams this charm will make operating any charm requiring SMTP
authentication simple and straightforward through Juju's clean interface.

## Project and community

The SMTP Integrator Operator is a member of the Ubuntu family. It's an open source
project that warmly welcomes community projects, contributions, suggestions,
fixes and constructive feedback.
* [Code of conduct](https://ubuntu.com/community/code-of-conduct)
* [Get support](https://discourse.charmhub.io/)
* [Join our online chat](https://chat.charmhub.io/charmhub/channels/charm-dev)
* [Contribute](https://charmhub.io/smtp-integrator/docs/how-to-contribute)
Thinking about using the SMTP Integrator Operator for your next project? [Get in touch](https://chat.charmhub.io/charmhub/channels/charm-dev)!

## Contributing to this documentation

Documentation is an important part of this project, and we take the same open-source approach to the documentation as the code. As such, we welcome community contributions, suggestions and constructive feedback on our documentation. Our documentation is hosted on the [Charmhub forum](https://charmhub.io/smtp-integrator/docs) to enable easy collaboration. Please use the "Help us improve this documentation" links on each documentation page to either directly change something you see that's wrong, ask a question, or make a suggestion about a potential change via the comments section.

If there's a particular area of documentation that you'd like to see that's missing, please [file a bug](https://github.com/canonical/smtp-integrator-operator/issues).

---

For further details,
[see the charm's detailed documentation](https://charmhub.io/smtp-integrator/docs).

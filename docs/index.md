SMTP Integrator is an integrator charm for providing SMTP configuration details to consumer charms which seek to authenticate using an SMTP server.

Like any Juju charm, SMTP Integrator supports one-line deployment, configuration, and integration. Configure the SMTP endpoint once in the integrator charm, then integrate any number of consumer charms to share those details over a Juju integration. This keeps SMTP credentials in a single, centrally managed place. The charm can be deployed on both Kubernetes and machine substrates.

This charm will make SMTP configuration straightforward for DevOps and SRE teams through Juju's clean interface.


## In this documentation

| | |
|--|--|
| **Get started** | [Deploy the SMTP integrator charm](https://charmhub.io/smtp-integrator/docs/tutorial-getting-started) |
| **Deployment** | [Configure SMTP](https://charmhub.io/smtp-integrator/docs/how-to-configure-smtp) • [Configurations](https://charmhub.io/smtp-integrator/docs/reference-configurations) • [Integrations](https://charmhub.io/smtp-integrator/docs/reference-integrations) |
| **Operations** | [Upgrade](https://charmhub.io/smtp-integrator/docs/how-to-upgrade) • [Actions](https://charmhub.io/smtp-integrator/docs/reference-actions) |
| **Design** | [Charm architecture](https://charmhub.io/smtp-integrator/docs/reference-charm-architecture) |

## How this documentation is organized

This documentation uses the [Diátaxis documentation structure](https://diataxis.fr/).

* The [Tutorial](https://charmhub.io/smtp-integrator/docs/tutorial-getting-started) takes you step-by-step through your first deployment of the SMTP Integrator charm.
* The [How-to guides](https://charmhub.io/smtp-integrator/docs/how-to-configure-smtp) cover practical tasks such as configuring SMTP, upgrading, and contributing to the charm.
* The [Reference](https://charmhub.io/smtp-integrator/docs/reference-actions) material provides technical details on actions, configurations, integrations, and charm architecture.

## Contributing to this documentation

Documentation is an important part of this project, and we take the same open-source approach to the documentation as the code. As such, we welcome community contributions, suggestions and constructive feedback on our documentation. Our documentation is hosted on the [Charmhub forum](https://charmhub.io/smtp-integrator/docs) to enable easy collaboration. Please use the "Help us improve this documentation" links on each documentation page to either directly change something you see that's wrong, ask a question, or make a suggestion about a potential change via the comments section.

If there's a particular area of documentation that you'd like to see that's missing, please [file a bug](https://github.com/canonical/smtp-integrator-operator/issues).

## Project and community

The SMTP Integrator Operator is a member of the Ubuntu family. It's an open source
project that warmly welcomes community projects, contributions, suggestions,
fixes and constructive feedback.

The code is licensed under the [Apache License, version 2](https://www.apache.org/licenses/LICENSE-2.0), and pull requests are accepted once you've signed a [Contributor License Agreement](https://en.wikipedia.org/wiki/Contributor_License_Agreement).

* [Code of conduct](https://ubuntu.com/community/code-of-conduct)
* [File a bug](https://github.com/canonical/smtp-integrator-operator/issues)
* Get support through the [Discourse forum](https://discourse.charmhub.io/)
* [Join our online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)
* [Contribute](https://charmhub.io/smtp-integrator/docs/how-to-contribute)

Thinking about using the SMTP Integrator Operator for your next project? [Get in touch](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)!

# Contents

1. [How To](how-to)
  1. [How to configure SMTP](how-to/configure-smtp.md)
  1. [How to contribute](how-to/contribute.md)
  1. [How to upgrade](how-to/upgrade.md)
1. [Reference](reference)
  1. [Actions](reference/actions.md)
  1. [Charm architecture](reference/charm-architecture.md)
  1. [Configurations](reference/configurations.md)
  1. [Integrations](reference/integrations.md)
1. [Tutorial](tutorial)
  1. [Getting started](tutorial/getting-started.md)

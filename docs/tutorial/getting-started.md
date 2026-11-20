# Deploy the SMTP Integrator charm for the first time

The SMTP Integrator charm doesn't send emails itself. Instead, it stores the
details of an outgoing SMTP relay, such as its host, port and credentials, and
shares them with other charms through the `smtp` integration. This lets you
configure SMTP once and reuse it across any number of consumer charms.

In this tutorial, you'll deploy the SMTP Integrator charm on Kubernetes,
configure it, and integrate it with a consumer charm to see the SMTP details
being shared. The charm can also be deployed on a machine substrate, but this
tutorial uses Kubernetes.

## What you'll do

1. Deploy the SMTP Integrator charm.
2. Configure the SMTP relay host.
3. Deploy a consumer charm.
4. Integrate the two charms and verify the shared SMTP details.
5. Clean up the environment.

## What you'll need

You will need a working station, such as a laptop, with AMD64 architecture. Your
working station should have at least 4 CPU cores, 8 GB of RAM, and 50 GB of
disk space.

> **Tip:** You can use Multipass to create an isolated environment by running:
>
> 
> multipass launch 24.04 --name charm-tutorial-vm --cpus 4 --memory 8G --disk 50G
> ```

This tutorial requires the following software to be installed on your working
station (either locally or in the Multipass VM):

- Juju 3
- Canonical Kubernetes
- `jq`

Install `jq`, which you'll use later to package the consumer charm's code:

```
sudo snap install jq
```

Use [Concierge](https://github.com/canonical/concierge) to set up Juju and
Canonical Kubernetes:

```
sudo snap install --classic concierge
sudo concierge prepare -p k8s
```

The first command installs Concierge, and the second command uses Concierge to
install and configure Juju and Kubernetes.

For this tutorial, Juju must be bootstrapped to a Kubernetes controller.
Concierge should complete this step for you. You can verify this by checking
for `msg="Bootstrapped Juju" provider=k8s` in the terminal output and by
running `juju controllers`.

If Concierge did not perform the bootstrap, run:

```
juju bootstrap k8s tutorial-controller
```

To work inside the Multipass VM, log in with the following command:

```
multipass shell charm-tutorial-vm
```

> **Note:** If you're working locally, you don't need to do this step.

## Set up the environment

To manage resources effectively and to separate this tutorial's workload from
your usual work, create a new model in the Kubernetes controller:

```
juju add-model smtp-tutorial
```

## Deploy the charm

Deploy the SMTP Integrator charm from Charmhub:

```
juju deploy smtp-integrator
```

Run `juju status` to check the current state of the deployment. After a minute
or so, the output should be similar to the following:

```
Model          Controller     Cloud/Region  Version  SLA          Timestamp
smtp-tutorial  concierge-k8s  k8s           3.6.29   unsupported  09:51:30+03:00

App              Version  Status   Scale  Charm            Channel        Rev  Address         Exposed  Message
smtp-integrator           blocked      1  smtp-integrator  latest/stable  121  10.152.183.234  no       invalid configuration: host

Unit                Workload  Agent  Address     Ports  Message
smtp-integrator/0*  blocked   idle   10.1.0.169         invalid configuration: host
```

The charm is in `blocked` status with the message `invalid configuration: host`.
This is expected: the charm can't share any SMTP details until it knows which
SMTP relay to point to.

## Configure the SMTP relay

The `host` configuration option is the only mandatory one. It's the hostname or
IP address of the outgoing SMTP relay, that is, the mail server that consumer
charms will connect to when sending emails. In a real deployment, this would be
your organization's mail server or a hosted email provider.

For this tutorial, use the placeholder `smtp.example.com`:

```
juju config smtp-integrator host=smtp.example.com
```

Run `juju status` again. The charm should now be `active`:

```
Model          Controller     Cloud/Region  Version  SLA          Timestamp
smtp-tutorial  concierge-k8s  k8s           3.6.29   unsupported  09:51:53+03:00

App              Version  Status  Scale  Charm            Channel        Rev  Address         Exposed  Message
smtp-integrator           active      1  smtp-integrator  latest/stable  121  10.152.183.234  no

Unit                Workload  Agent  Address     Ports  Message
smtp-integrator/0*  active    idle   10.1.0.169
```

The charm also accepts other options, such as `port` (defaults to `25`),
`auth_type`, `user`, `password_secret`, `transport_security` and `domain`.
You'll change some of them later in this tutorial. For the full list, see the
[configurations reference](../reference/configurations.md).

## Deploy a consumer charm

To see the SMTP Integrator charm in action, you need a charm that consumes the
`smtp` integration. In a real deployment, this would be an application that
sends emails. For this tutorial, you'll use
[any-charm](https://charmhub.io/any-charm), a test charm whose code you can
inject through its configuration.

Create a file named `any_charm.py` with the following content:

```python
from any_charm_base import AnyCharmBase
from charmlibs.interfaces import smtp


class AnyCharm(AnyCharmBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smtp = smtp.SmtpRequires(self)

    def get_smtp_env(self):
        data = self.smtp.get_relation_data()
        if data is None:
            return {}
        return {
            "SMTP_HOST": data.host,
            "SMTP_PORT": str(data.port),
            "SMTP_AUTH_TYPE": data.auth_type.value,
            "SMTP_TRANSPORT_SECURITY": data.transport_security.value,
        }
```

This code uses the `SmtpRequires` class from the
[`charmlibs-interfaces-smtp`](https://pypi.org/project/charmlibs-interfaces-smtp/)
library to make the charm a consumer of the `smtp` relation. The
`get_smtp_env` method reads the SMTP details received through the relation
and turns them into environment variables, the same way a real application
would consume them.

Deploy any-charm with the name `smtp-consumer`:

```
juju deploy any-charm smtp-consumer \
  --channel beta \
  --base ubuntu@24.04 \
  --config src-overwrite="$(jq -n --rawfile c any_charm.py '{"any_charm.py": $c}')" \
  --config python-packages="charmlibs-interfaces-smtp"
```

The `src-overwrite` option injects your `any_charm.py` file into the charm, and
the `python-packages` option installs the `charmlibs-interfaces-smtp` library
from PyPI.

The command uses `jq` to package the file into the format that `src-overwrite`
expects.

Installing the Python packages can take a few minutes. Wait until
`smtp-consumer` reaches `active` status in `juju status`.

## Integrate the charms

The SMTP Integrator charm provides two endpoints: `smtp`, which shares
passwords through Juju secrets, and `smtp-legacy`, which shares them in plain
relation data for older consumers. Integrate the consumer with the `smtp`
endpoint:

```
juju integrate smtp-integrator:smtp smtp-consumer:smtp
```

Run `juju status --relations` to check the relation:

```
Model          Controller     Cloud/Region  Version  SLA          Timestamp
smtp-tutorial  concierge-k8s  k8s           3.6.29   unsupported  09:53:20+03:00

App              Version  Status  Scale  Charm            Channel        Rev  Address         Exposed  Message
smtp-consumer             active      1  any-charm        latest/beta    183  10.152.183.210  no
smtp-integrator           active      1  smtp-integrator  latest/stable  121  10.152.183.234  no

Unit                Workload  Agent  Address     Ports  Message
smtp-consumer/0*    active    idle   10.1.0.98
smtp-integrator/0*  active    idle   10.1.0.169

Integration provider        Requirer                    Interface      Type     Message
smtp-consumer:peer-any      smtp-consumer:peer-any      peer-any       peer
smtp-integrator:smtp        smtp-consumer:smtp          smtp           regular
smtp-integrator:smtp-peers  smtp-integrator:smtp-peers  smtp-instance  peer
```

The `smtp-integrator:smtp` to `smtp-consumer:smtp` line shows that the
relation is established.

## Verify the shared SMTP details

Check the SMTP details that the consumer has received by calling the
`get_smtp_env` method through any-charm's `rpc` action:

```
juju run smtp-consumer/0 rpc method=get_smtp_env
```

The output should be similar to the following:

```
return: '{"SMTP_HOST": "smtp.example.com", "SMTP_PORT": "25", "SMTP_AUTH_TYPE": "none",
  "SMTP_TRANSPORT_SECURITY": "none"}'
```

The consumer received the `host` you configured, along with the default values
of the other options.

Now change the relay's port and transport security on the SMTP Integrator
charm:

```
juju config smtp-integrator port=587 transport_security=starttls
```

Wait a few seconds and run the `rpc` action again:

```
juju run smtp-consumer/0 rpc method=get_smtp_env
```

The environment variables reflect the new configuration:

```
return: '{"SMTP_HOST": "smtp.example.com", "SMTP_PORT": "587", "SMTP_AUTH_TYPE": "none",
  "SMTP_TRANSPORT_SECURITY": "starttls"}'
```

Every consumer integrated with the SMTP Integrator charm receives configuration
changes automatically, without any action on the consumer side.

## Clean up the environment

Congratulations! You successfully deployed the SMTP Integrator charm,
configured an SMTP relay and shared its details with a consumer charm.

To remove the model and everything deployed in it, run:

```
juju destroy-model smtp-tutorial --destroy-storage --no-prompt
```

If you used a Multipass VM, you can remove it with:

```
multipass delete --purge charm-tutorial-vm
```

For more options, see
[Tear down your test environment](https://documentation.ubuntu.com/juju/3.6/howto/manage-your-juju-deployment/tear-down-your-juju-deployment-local-testing-and-development/).

## Next steps

You achieved a basic deployment of the charm. If you want to go further in your
deployment or learn more about the charm, check out these pages:

- [Configure SMTP](../how-to/configure-smtp.md) with authentication and
  transport security for a real SMTP relay.
- [Upgrade](../how-to/upgrade.md) the charm to a newer revision.
- Learn about all the available [configurations](../reference/configurations.md)
  and [integrations](../reference/integrations.md).
- Understand the [charm architecture](../reference/charm-architecture.md).

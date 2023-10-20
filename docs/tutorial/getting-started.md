# Getting started

In this tutorial, we'll walk you through the process of deploying the SMTP Integrator charm. We'll be deploying the charm on top of Kubernetes although a machine substrate could also be used.

## Requirements

You will need:

* A laptop or desktop running Ubuntu (or you can use a VM).
* [Juju and Microk8s](https://juju.is/docs/olm/microk8s) installed.

## Deploy this charm

The charm will the deployed in a new model named `smtp-tutorial`:

```
# Add the model
juju add-model smtp-tutorial

# Deploy the charm
juju deploy smtp-integrator

# Provide the mandatory configurations
juju config smtp-integrator host=smtp.example.com

```

By running `juju status --relations` the current state of the deployment can be queried, with the charm eventually reaching `Active` state:
```
Model           Controller          Cloud/Region        Version  SLA          Timestamp
smtp-tutorial   microk8s-localhost  microk8s/localhost  2.9.44   unsupported  12:54:25+02:00

App              Version  Status  Scale  Charm            Channel  Rev  Address        Exposed  Message
smtp-integrator           active      1  smtp-integrator             0  10.152.183.65  no       

Unit                Workload  Agent  Address     Ports  Message
smtp-integrator/0*  active    idle   10.1.57.14    

```

Run `kubectl get pods -n smtp-tutorial` to see the pods that are being created by the charms:
```
NAME                            READY   STATUS    RESTARTS   AGE
modeloperator-d465f6695-zvhk8   1/1     Running   0          2m33s
smtp-integrator-0               1/1     Running   0          99s

```

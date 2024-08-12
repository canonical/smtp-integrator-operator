<!-- markdownlint-disable -->

<a href="../src/charm_state.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `charm_state.py`
Module defining the CharmState class which represents the state of the SMTP Integrator charm. 



---

## <kbd>class</kbd> `CharmConfigInvalidError`
Exception raised when a charm configuration is found to be invalid. 



**Attributes:**
 
 - <b>`msg`</b> (str):  Explanation of the error. 

<a href="../src/charm_state.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(msg: str)
```

Initialize a new instance of the CharmConfigInvalidError exception. 



**Args:**
 
 - <b>`msg`</b> (str):  Explanation of the error. 





---

## <kbd>class</kbd> `CharmState`
Represents the state of the SMTP Integrator charm. 



**Attributes:**
 
 - <b>`host`</b>:  The hostname or IP address of the outgoing SMTP relay. 
 - <b>`port`</b>:  The port of the outgoing SMTP relay. 
 - <b>`user`</b>:  The SMTP AUTH user to use for the outgoing SMTP relay. 
 - <b>`password`</b>:  The SMTP AUTH password to use for the outgoing SMTP relay. 
 - <b>`auth_type`</b>:  The type used to authenticate with the SMTP relay. 
 - <b>`transport_security`</b>:  The security protocol to use for the outgoing SMTP relay. 
 - <b>`domain`</b>:  The domain used by the emails sent from SMTP relay. 
 - <b>`skip_ssl_verify`</b>:  Specifies if certificate trust verification is skipped in the SMTP relay. 

<a href="../src/charm_state.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(smtp_integrator_config: SmtpIntegratorConfig)
```

Initialize a new instance of the CharmState class. 



**Args:**
 
 - <b>`smtp_integrator_config`</b>:  SMTP Integrator configuration. 




---

<a href="../src/charm_state.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_charm`

```python
from_charm(charm: 'CharmBase') → CharmState
```

Initialize a new instance of the CharmState class from the associated charm. 



**Args:**
 
 - <b>`charm`</b>:  The charm instance associated with this state. 

Return: The CharmState instance created by the provided charm. 



**Raises:**
 
 - <b>`CharmConfigInvalidError`</b>:  if the charm configuration is invalid. 


---

## <kbd>class</kbd> `SmtpIntegratorConfig`
Represent charm builtin configuration values. 



**Attributes:**
 
 - <b>`host`</b>:  The hostname or IP address of the outgoing SMTP relay. 
 - <b>`port`</b>:  The port of the outgoing SMTP relay. 
 - <b>`user`</b>:  The SMTP AUTH user to use for the outgoing SMTP relay. 
 - <b>`password`</b>:  The SMTP AUTH password to use for the outgoing SMTP relay. 
 - <b>`auth_type`</b>:  The type used to authenticate with the SMTP relay. 
 - <b>`transport_security`</b>:  The security protocol to use for the outgoing SMTP relay. 
 - <b>`domain`</b>:  The domain used by the emails sent from SMTP relay. 
 - <b>`skip_ssl_verify`</b>:  Specifies if certificate trust verification is skipped in the SMTP relay. 


---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation. 



**Returns:**
  A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`. 

---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance. 



**Returns:**
  A set of strings representing the fields that have been set,  i.e. that were not filled from defaults. 





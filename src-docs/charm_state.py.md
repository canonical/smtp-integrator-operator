<!-- markdownlint-disable -->

<a href="../src/charm_state.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `charm_state.py`
Module defining the CharmState class which represents the state of the SMTP Integrator charm. 

**Global Variables**
---------------
- **KNOWN_CHARM_CONFIG**


---

## <kbd>class</kbd> `CharmConfigInvalidError`
Exception raised when a charm configuration is found to be invalid. 

Attrs:  msg (str): Explanation of the error. 

<a href="../src/charm_state.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

Attrs:  host: The hostname or IP address of the outgoing SMTP relay.  port: The port of the outgoing SMTP relay.  user: The SMTP AUTH user to use for the outgoing SMTP relay.  password: The SMTP AUTH password to use for the outgoing SMTP relay.  auth_type: The type used to authenticate with the SMTP relay.  transport_security: The security protocol to use for the outgoing SMTP relay.  domain: The domain used by the sent emails from SMTP relay. 

<a href="../src/charm_state.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(smtp_integrator_config: SmtpIntegratorConfig)
```

Initialize a new instance of the CharmState class. 



**Args:**
 
 - <b>`smtp_integrator_config`</b>:  SMTP Integrator configuration. 


---

#### <kbd>property</kbd> auth_type

Return auth_type config. 



**Returns:**
 
 - <b>`AuthType`</b>:  auth_type config. 

---

#### <kbd>property</kbd> domain

Return domain config. 



**Returns:**
 
 - <b>`str`</b>:  domain config. 

---

#### <kbd>property</kbd> host

Return host config. 



**Returns:**
 
 - <b>`str`</b>:  host config. 

---

#### <kbd>property</kbd> password

Return password config. 



**Returns:**
 
 - <b>`str`</b>:  password config. 

---

#### <kbd>property</kbd> port

Return port config. 



**Returns:**
 
 - <b>`int`</b>:  port config. 

---

#### <kbd>property</kbd> transport_security

Return transport_security config. 



**Returns:**
 
 - <b>`TransportSecurity`</b>:  transport_security config. 

---

#### <kbd>property</kbd> user

Return user config. 



**Returns:**
 
 - <b>`str`</b>:  user config. 



---

<a href="../src/charm_state.py#L148"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

Attrs:  host: The hostname or IP address of the outgoing SMTP relay.  port: The port of the outgoing SMTP relay.  user: The SMTP AUTH user to use for the outgoing SMTP relay.  password: The SMTP AUTH password to use for the outgoing SMTP relay.  auth_type: The type used to authenticate with the SMTP relay.  transport_security: The security protocol to use for the outgoing SMTP relay.  domain: The domain used by the sent emails from SMTP relay. 





# Contributing

## Database

On a new database, if you want to install the database with migrations :

```python
import os
os.environ['TEST_DATABASE_INSTALL_GOBS'] = '0.2.2'  # Enable
del os.environ['TEST_DATABASE_INSTALL_GOBS']  # Disable
```
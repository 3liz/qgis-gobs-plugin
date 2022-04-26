# Contributing

## Documentation

The documentation is using [MkDocs](https://www.mkdocs.org/) with [Material](https://squidfunk.github.io/mkdocs-material/) :

```bash
pip install -r requirements/doc.txt
mkdocs serve
```

## Database

On a new database, if you want to install the database with migrations :

```python
import os
os.environ['TEST_DATABASE_INSTALL_GOBS'] = '0.2.2'  # Enable
del os.environ['TEST_DATABASE_INSTALL_GOBS']  # Disable
```
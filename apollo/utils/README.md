# 🔧 apollo/utils

Shared helpers used across the whole Apollo codebase.

## Files

| File | Purpose |
|------|---------|
| `config.py` | Loads `.env` API keys and settings into a typed config object |
| `logger.py` | Centralized logging setup — import `get_logger` from here |

## Usage

```python
from apollo.utils.config import Config
from apollo.utils.logger import get_logger

logger = get_logger(__name__)
config = Config()

logger.info(f"Using model: {config.anthropic_api_key[:8]}...")
```

## Adding new utilities

If you find yourself copy-pasting a helper across multiple modules, it belongs here.
Keep each utility in its own file with a clear, single responsibility.

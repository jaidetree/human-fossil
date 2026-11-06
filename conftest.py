"""Root pytest conftest.

Playwright's sync API drives its event loop via greenlet-based context
switching in the calling thread rather than a separate one, which makes
`asyncio.get_running_loop()` report a loop as running even for the plain
synchronous test code in `tests/test_playwright_golden_paths.py`. Django's
`SynchronousOnlyOperation` guard (`django/utils/asyncio.py`) then refuses ORM
access — e.g. `pytest-django`'s own `live_server`/test-db setup — even though
nothing is actually happening concurrently. This is a documented false
positive when combining pytest-django with pytest-playwright's sync fixtures;
`DJANGO_ALLOW_ASYNC_UNSAFE` is Django's own escape hatch for exactly this
case.
"""

import os

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "1")

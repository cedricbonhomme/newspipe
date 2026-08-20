import os

# newspipe.bootstrap reads this at import time; tests only need the config to be
# loadable (for CRAWLER_TIMEOUT / CRAWLER_USER_AGENT), not a populated database.
os.environ.setdefault("NEWSPIPE_CONFIG", "sqlite.py")

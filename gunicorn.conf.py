"""Gunicorn WSGI server configuration for Smart Agriculture Agent on Render.

Tuned for Render free tier (~512 MB RAM) running a PyTorch MobileNetV2 model.

Key design decisions:
  workers = 1
    A single worker is sufficient and safe. The MobileNetV2 model uses ~55-70 MB
    RAM. With Flask overhead, SQLite, and Python runtime the process footprint is
    ~250-350 MB, leaving headroom within the 512 MB limit. More workers would
    each load their own model copy and exceed available memory.

  preload_app = True
    Loads the Flask app (but NOT the model weights — they are lazy-loaded) in
    the Gunicorn master process before forking workers. This means:
      • Module imports and blueprint registration happen once.
      • SQLite schema init and demo-user seeding happen once.
      • Workers inherit the already-initialized app via fork copy-on-write.
    The model itself is NOT preloaded here because lazy loading means it is
    only loaded in the worker on the first predict() call, which is correct.

  timeout = 120
    Default Gunicorn timeout is 30 s. MobileNetV2 CPU inference on a cold-started
    Render free-tier instance can take 5-15 s for the first request (lazy load).
    120 s provides enough headroom without masking genuine hangs.

  worker_class = "sync"
    Synchronous workers are appropriate for a CPU-bound inference workload.
    Async workers (gevent/eventlet) do not help and add complexity.

  threads = 2
    Two threads per worker lets the single process serve a second request
    (e.g. a static asset or health check) while inference is running,
    without the memory cost of a second full worker process.

  keepalive = 5
    Allows Render's load balancer to reuse TCP connections.

  max_requests / max_requests_jitter
    Recycles the worker after 500 requests (±50 jitter) to prevent slow
    memory creep from Pillow image buffers or torch tensor allocations
    that are not freed promptly by the garbage collector.
"""

import os

# Binding
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Worker configuration — 1 worker is intentional for memory-constrained Render
workers = 1
threads = 2
worker_class = "sync"

# Preload the Flask app in master before forking workers
preload_app = True

# Timeout tuned for cold-start lazy model load (first inference ~5-15 s on CPU)
timeout = 120
graceful_timeout = 30
keepalive = 5

# Worker recycling to prevent slow memory accumulation
max_requests = 500
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"   # stdout
errorlog = "-"    # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)s μs'

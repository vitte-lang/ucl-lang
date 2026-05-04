<<< =========================================================
   UCL Example — Full configuration (dev / prod / staging)
   ========================================================= >>>

# -------------------------
# Base config
# -------------------------

app {
  name = "vitte-core"
  version = "1.0.0"
  debug = true
}

server {
  host = "0.0.0.0"
  base_port = 8000
  port = $base_port + 1
}

# -------------------------
# Environment binding
# -------------------------

env_config {
  env = env("APP_ENV")
  is_prod = $env == "prod"
}

# -------------------------
# Database config
# -------------------------

database {
  host = env("DB_HOST")
  port = 5432
  user = "admin"
  password = env("DB_PASS")

  pool {
    min = 2
    max = if $env_config.is_prod { 20 } else { 5 }
  }
}

# -------------------------
# Feature flags
# -------------------------

features {
  caching = true
  metrics = true
  experimental = false
}

# -------------------------
# Profiles
# -------------------------

profile dev {
  app.debug = true
  server.port = 8001
  database.pool.max = 5
  features.experimental = true
}

profile staging {
  app.debug = false
  server.port = 9001
  database.pool.max = 10
}

profile prod {
  app.debug = false
  server.port = 80
  database.pool.max = 50
  features.experimental = false
}

# -------------------------
# Conditional override
# -------------------------

if $env_config.is_prod {
  server.host = "prod.internal"
  features.metrics = true
} else {
  server.host = "localhost"
}

# -------------------------
# Collections
# -------------------------

allowed_ips = [
  "127.0.0.1",
  "192.168.1.10",
  "10.0.0.0/8"
]

services = {
  api: "http://localhost:8001",
  auth: "http://localhost:8002"
}

# -------------------------
# Macro (reusable logic)
# -------------------------

macro scale_pool(base, factor) {
  give base * factor
}

database.pool.scaled = scale_pool(database.pool.max, 2)

# -------------------------
# Template (structure reuse)
# -------------------------

template service_block {
  timeout = 30
  retries = 3
}

service_a {
  use service_block
  url = "http://service-a"
}

service_b {
  use service_block
  url = "http://service-b"
}

# -------------------------
# Include external config
# -------------------------

include "secrets.ucl"

# -------------------------
# Schema validation
# -------------------------

schema app_schema {
  app.name: string [required]
  app.version: string [required]

  server.port: number [min(1), max(65535)]

  database.host: string [required]
  database.port: number [min(1), max(65535)]

  database.pool.max: number [min(1)]
}

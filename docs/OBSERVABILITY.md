# Observability Stack

Production-grade observability for Systems Design Lab - visualize exactly what happens when simulator scenarios inject failures.

## Stack Components

| Component      | Purpose                    | Port | Dashboard URL         |
| -------------- | -------------------------- | ---- | --------------------- |
| **Prometheus** | Metrics collection         | 9090 | http://localhost:9090 |
| **Grafana**    | Dashboards & visualization | 3000 | http://localhost:3000 |
| **Loki**       | Log aggregation            | 3100 | _(via Grafana)_       |
| **Tempo**      | Distributed tracing        | 3200 | _(via Grafana)_       |
| **Promtail**   | Log shipping to Loki       | -    | -                     |

## Quick Start

### 1. Start Observability Stack

```bash
make up        # Starts all services including observability
make status    # Verify all services are healthy
```

### 2. Open Grafana Dashboards

```bash
make grafana   # Opens http://localhost:3000
```

**Login:** `admin` / `admin`

**Available Dashboards:**

- **System Metrics** - HTTP request rate, latency (p95), error rates, logs
- **Simulator Scenarios** - Active scenarios, injection rates, effect durations

### 3. View Metrics Directly

```bash
make metrics      # Fetch raw Prometheus metrics from backend
make prometheus   # Open Prometheus UI
```

## What Gets Observed

### HTTP Metrics (Prometheus)

Automatically collected for all HTTP requests:

- `http_requests_total` - Total requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram (p50, p95, p99)

### Simulator Metrics (Prometheus)

Tracks scenario behavior:

- `simulator_scenarios_enabled` - Which scenarios are currently active (gauge)
- `simulator_scenarios_active_total` - Total scenario activations (counter)
- `simulator_injections_total` - Injections applied by scenario and effect type
- `simulator_effect_duration_seconds` - Time to apply effects

### Structured Logs (Loki)

JSON-formatted logs with correlation:

- `request_id` - Unique per request
- `trace_id` - OpenTelemetry trace ID
- `span_id` - OpenTelemetry span ID
- Standard fields: `timestamp`, `level`, `message`

View in **Grafana → Explore → Loki** or in dashboard "Application Logs" panel.

### Distributed Traces (Tempo)

End-to-end request tracing:

- FastAPI automatic instrumentation
- SQLAlchemy query tracing (when DB used)
- Correlated with logs via `trace_id`

View in **Grafana → Explore → Tempo** or click "Trace ID" links in logs.

## Grafana Dashboards

### 1. System Metrics Dashboard

Shows overall application health:

- **HTTP Request Rate** - req/s over time by endpoint
- **HTTP Request Duration (p95)** - Latency gauge with thresholds (green < 100ms, yellow < 500ms, red > 1s)
- **HTTP 5xx Error Rate** - Server errors by endpoint
- **Application Logs** - Recent logs from backend

**Use case:** Baseline health monitoring

### 2. Simulator Scenarios Dashboard

Visualizes scenario impact:

- **Active Scenarios** - Timeline showing which scenarios are enabled
- **Scenario Injection Rate** - How often effects are applied (by scenario and effect type)
- **Scenario Effect Duration (p95)** - Time to apply effects
- **Simulator Logs** - Filtered logs containing "simulator" or "scenario"

**Use case:** Observe scenario behavior in real-time, debug unexpected effects

## Example: Observing a Scenario

### Enable Fixed Latency Scenario

```bash
# Via frontend
# http://localhost:5173 → Enable "fixed-latency" with ms=500

# Or via API
curl -X POST http://localhost:8000/api/sim/enable \
  -H "Content-Type: application/json" \
  -d '{"name": "fixed-latency", "parameters": {"ms": 500}, "duration_seconds": 300}'
```

### Watch in Grafana

1. **System Metrics Dashboard:**
   - HTTP Request Duration (p95) jumps to ~500ms
   - HTTP Request Rate may decrease (clients timing out)

2. **Simulator Scenarios Dashboard:**
   - "Active Scenarios" shows `fixed-latency = 1`
   - "Scenario Injection Rate" shows injections/sec
   - Logs show "Simulated delay applied"

3. **Prometheus (Advanced):**
   - Query: `http_request_duration_seconds{endpoint="/api/sim/status"}`
   - See histogram buckets with latency distribution

4. **Tempo Traces:**
   - Click a trace ID from logs → see span timeline
   - Artificial delay visible as a span segment

## Configuration

### Environment Variables (Backend)

Set in [docker-compose.yml](../docker-compose.yml):

```yaml
environment:
  LOG_LEVEL: INFO # DEBUG | INFO | WARNING | ERROR
  LOG_JSON: "true" # true = JSON logs (for Loki), false = human-readable
  OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317
  OTEL_SERVICE_NAME: systems-design-lab-backend
```

### Prometheus Scrape Interval

Edit [observability/prometheus/prometheus.yml](../observability/prometheus/prometheus.yml):

```yaml
scrape_configs:
  - job_name: "backend"
    scrape_interval: 10s # Change to 5s for more frequent metrics
```

### Grafana Datasources

Auto-provisioned in [observability/grafana/provisioning/datasources/datasources.yml](../observability/grafana/provisioning/datasources/datasources.yml).

To add new datasource:

1. Add to `datasources.yml`
2. Restart: `make down && make up`

### Dashboard Customization

Dashboards are in [observability/grafana/dashboards/](../observability/grafana/dashboards/):

- `system-metrics.json` - General application metrics
- `simulator-scenarios.json` - Simulator-specific metrics

Edit JSON files directly or:

1. Modify in Grafana UI
2. Export JSON: Dashboard → Share → Export → Save to `observability/grafana/dashboards/`
3. Commit to version control

**Dashboards auto-reload** on file change (10s interval).

## Retention & Storage

Configured for local development:

| Component  | Retention  | Storage Location                |
| ---------- | ---------- | ------------------------------- |
| Prometheus | 7 days     | Docker volume `prometheus_data` |
| Loki       | 7 days     | Docker volume `loki_data`       |
| Tempo      | 48 hours   | Docker volume `tempo_data`      |
| Grafana    | Persistent | Docker volume `grafana_data`    |

To clear observability data:

```bash
make reset   # Removes ALL volumes (including Postgres!)
```

To clear only observability volumes:

```bash
docker-compose down
docker volume rm systems_design_lab_prometheus_data
docker volume rm systems_design_lab_loki_data
docker volume rm systems_design_lab_tempo_data
docker-compose up -d
```

## Troubleshooting

### Metrics Endpoint Not Working

```bash
# Check backend is running
make status

# Check metrics endpoint
curl http://localhost:8000/api/metrics

# Should return Prometheus text format:
# http_requests_total{endpoint="/api/health",method="GET",status="200"} 42.0
```

### No Logs in Loki

1. Check Promtail is running: `docker ps | grep promtail`
2. Check backend logs are JSON: `docker-compose logs backend | head -n 5`
   - Should see `{"timestamp": ..., "level": "INFO", ...}`
   - If not, set `LOG_JSON=true` in docker-compose.yml
3. Check Promtail config: [observability/promtail/promtail-config.yml](../observability/promtail/promtail-config.yml)

### No Traces in Tempo

1. Check Tempo is running: `docker ps | grep tempo`
2. Check OTLP endpoint: `docker-compose logs backend | grep -i otel`
3. Backend should connect to `http://tempo:4317` (gRPC)
4. If warnings about "Failed to setup OpenTelemetry", Tempo may not be reachable

### Grafana Dashboards Not Loading

1. Check provisioning: `docker-compose logs grafana | grep provision`
2. Verify files exist:
   ```bash
   ls observability/grafana/provisioning/datasources/
   ls observability/grafana/dashboards/
   ```
3. Restart Grafana: `docker-compose restart grafana`

### High Memory Usage

Observability stack adds ~1-2GB RAM overhead. To reduce:

1. Lower Prometheus retention:

   ```yaml
   # observability/prometheus/prometheus.yml
   --storage.tsdb.retention.time=1d # Instead of 7d
   ```

2. Reduce scrape frequency:

   ```yaml
   scrape_interval: 30s # Instead of 10s
   ```

3. Run observability stack only when needed:

   ```bash
   # Start only app services
   docker-compose up -d postgres backend frontend

   # Start observability separately
   docker-compose up -d prometheus grafana loki tempo promtail
   ```

## Architecture

### Clean Architecture Compliance

Observability instrumentation respects Clean Architecture boundaries:

```
domain/              # NO observability imports
application/
  ports/
    metrics.py       # ✅ Port interface (abstract)
infrastructure/
  observability/
    metrics.py       # ✅ Prometheus adapter (concrete)
    logging.py       # ✅ JSON logging setup
    tracing.py       # ✅ OpenTelemetry setup
    middleware.py    # ✅ HTTP metrics middleware
api/
  main.py            # ✅ Wire up adapters (DI)
  routers/
    metrics.py       # ✅ /metrics endpoint
```

**Domain layer remains pure** - no Prometheus/OTEL imports.

### Metrics Flow

```
Request → RequestIdMiddleware (adds request_id)
        → ObservabilityMiddleware (tracks metrics, logs with trace_id)
        → SimulatorInjectionMiddleware (applies effects, emits injection metrics)
        → Route Handler
        → Response (ObservabilityMiddleware logs completion)
        → Prometheus scrapes /api/metrics endpoint
        → Grafana queries Prometheus
```

### Log Flow

```
Backend logs (JSON) → stdout
                    → Docker logs
                    → Promtail (scrapes Docker logs)
                    → Loki (stores logs)
                    → Grafana (queries Loki)
```

### Trace Flow

```
Request → OpenTelemetry instrumentation (creates trace)
        → Spans for each operation (FastAPI, SQLAlchemy, etc.)
        → OTLP exporter sends to Tempo (gRPC port 4317)
        → Tempo stores traces
        → Grafana queries Tempo (HTTP port 3200)
```

## Extending Observability

### Add Custom Metrics

1. Inject `MetricsPort` into your service:

   ```python
   from app.application.ports.metrics import MetricsPort

   class MyService:
       def __init__(self, metrics: MetricsPort):
           self._metrics = metrics

       def do_something(self):
           self._metrics.increment_counter("my_counter", {"label": "value"})
   ```

2. Wire in main.py:

   ```python
   metrics = PrometheusMetrics()
   my_service = MyService(metrics=metrics)
   ```

3. Metrics auto-registered: see [metrics.py](../backend/src/app/infrastructure/observability/metrics.py) `_register_application_metrics()`

### Add Custom Dashboard

1. Create JSON file: `observability/grafana/dashboards/my-dashboard.json`
2. Use existing dashboards as templates
3. Auto-loads on next Grafana start or after 10s

### Add Alerting

Grafana supports alerts on metrics/logs:

1. **In Dashboard:** Panel → Alert tab → Create alert rule
2. **Thresholds:** e.g., "p95 latency > 1s for 5 minutes"
3. **Notification channels:** Slack, email, webhook, etc.

See: https://grafana.com/docs/grafana/latest/alerting/

## Production Considerations

This stack is configured for **local development**. For production:

1. **Use managed services:** Grafana Cloud, Datadog, New Relic, etc.
2. **Secure Grafana:** Change default password, enable HTTPS
3. **Scale storage:** Use object storage (S3) for Loki/Tempo
4. **Add high availability:** Run Prometheus/Loki/Tempo replicas
5. **Implement sampling:** Trace 1-10% of requests instead of 100%
6. **Set up alerts:** On-call rotations, PagerDuty integration
7. **Compliance:** Log retention policies, PII scrubbing

## Makefile Commands

| Command           | Description                                  |
| ----------------- | -------------------------------------------- |
| `make grafana`    | Open Grafana dashboards in browser           |
| `make prometheus` | Open Prometheus UI in browser                |
| `make logs-obs`   | Tail observability stack logs                |
| `make metrics`    | Fetch raw metrics from backend /api/metrics  |
| `make up`         | Start all services (including observability) |
| `make down`       | Stop all services                            |
| `make reset`      | Stop and remove all volumes                  |

## Further Reading

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Tempo Documentation](https://grafana.com/docs/tempo/latest/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [The Three Pillars of Observability](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/ch04.html)

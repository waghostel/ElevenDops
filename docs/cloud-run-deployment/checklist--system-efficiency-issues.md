# System Efficiency Checklist for Cloud Deployments

This document catalogs common efficiency issues that affect system performance in serverless and containerized cloud environments. Use this as a pre-deployment optimization checklist.

---

## 1. Cold Start & Initialization

| ID         | Issue                                                     | Impact                                                       | Verification Strategy                                                                   |
| ---------- | --------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| `PERF-001` | Heavy module imports at startup                           | **High**. Increases cold start latency by seconds.           | Profile startup with `python -X importtime`. Lazy-load heavy modules (pandas, ML libs). |
| `PERF-002` | Database connections initialized synchronously on startup | **High**. Blocks first request until connection established. | Use connection pooling; initialize lazily on first use.                                 |
| `PERF-003` | No minimum instances configured                           | **Medium**. Every scale-from-zero incurs cold start.         | Cloud Run: `--min-instances=1`. Lambda: Provisioned Concurrency.                        |
| `PERF-004` | Large container image size                                | **Medium**. Slower pull times on cold start.                 | Use multi-stage builds; slim base images; exclude dev dependencies.                     |
| `PERF-005` | Synchronous secret fetching at startup                    | **Medium**. Blocks startup while calling Secret Manager.     | Use environment variable injection instead of runtime fetch.                            |

---

## 2. Database Performance

### Firestore / Firebase

| ID            | Issue                                            | Impact                                                 | Verification Strategy                                                   |
| ------------- | ------------------------------------------------ | ------------------------------------------------------ | ----------------------------------------------------------------------- |
| `DB-PERF-001` | N+1 query patterns                               | **High**. Multiplies read operations and latency.      | Audit code for loops containing `.get()`. Batch reads with `get_all()`. |
| `DB-PERF-002` | Missing composite indexes                        | **High**. Queries fail or perform full scans.          | Check Firestore console for index warnings. Deploy indexes in CI.       |
| `DB-PERF-003` | Reading entire documents when only fields needed | **Medium**. Wastes bandwidth and read costs.           | Use `select()` to fetch only required fields.                           |
| `DB-PERF-004` | Not using transactions for related writes        | **Medium**. Inconsistent data under concurrent access. | Wrap related writes in `batch()` or `transaction()`.                    |

### MongoDB

| ID            | Issue                               | Impact                                                    | Verification Strategy                                                       |
| ------------- | ----------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------- |
| `DB-PERF-010` | Missing indexes on query fields     | **High**. Full collection scans on every query.           | Use `explain()` to verify index usage. Create indexes for frequent queries. |
| `DB-PERF-011` | Unbounded queries without `limit()` | **High**. Returns millions of documents, exhausts memory. | Always add `.limit()` to queries. Implement pagination.                     |
| `DB-PERF-012` | Connection pool too small           | **Medium**. Requests queue waiting for connections.       | Increase `maxPoolSize` in connection string. Monitor connection wait times. |

### PostgreSQL / Cloud SQL

| ID            | Issue                                  | Impact                                                          | Verification Strategy                                   |
| ------------- | -------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------- |
| `DB-PERF-020` | SELECT \* instead of specific columns  | **Medium**. Transfers unnecessary data.                         | Audit queries; select only needed columns.              |
| `DB-PERF-021` | Missing connection pooling (PgBouncer) | **High**. Each request creates new connection (~50ms overhead). | Use Cloud SQL Proxy or PgBouncer. Verify pool hit rate. |
| `DB-PERF-022` | No query timeout configured            | **Medium**. Slow queries block connection pool.                 | Set `statement_timeout` in PostgreSQL config.           |

### DynamoDB

| ID            | Issue                       | Impact                                                | Verification Strategy                                |
| ------------- | --------------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| `DB-PERF-030` | Using Scan instead of Query | **Critical**. Reads entire table; expensive and slow. | Replace `scan()` with `query()` using partition key. |
| `DB-PERF-031` | Hot partition key design    | **High**. Throttling on specific partitions.          | Distribute writes with composite keys or suffixes.   |

---

## 3. Network & I/O

| ID             | Issue                                                       | Impact                                                  | Verification Strategy                                                |
| -------------- | ----------------------------------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------- |
| `NET-PERF-001` | Synchronous external API calls in request path              | **High**. Request latency = sum of all API latencies.   | Use `asyncio` for concurrent calls. Offload to background tasks.     |
| `NET-PERF-002` | No connection reuse (creating new HTTP clients per request) | **Medium**. TCP handshake overhead on every call.       | Reuse `httpx.Client` or `aiohttp.ClientSession` across requests.     |
| `NET-PERF-003` | Large payloads without compression                          | **Medium**. Increased bandwidth and latency.            | Enable gzip compression for API responses.                           |
| `NET-PERF-004` | Calling external APIs without timeout                       | **High**. Requests hang indefinitely on network issues. | Set explicit timeouts (`httpx.Timeout`). Implement circuit breakers. |

---

## 4. File & Storage Operations

| ID              | Issue                                               | Impact                                                       | Verification Strategy                                                     |
| --------------- | --------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `STOR-PERF-001` | Writing temp files to disk in serverless            | **High**. Disk I/O is slower than memory; may exhaust tmpfs. | Use `BytesIO` for in-memory file operations. ✅ _Fixed in this codebase._ |
| `STOR-PERF-002` | Downloading entire files when streaming is possible | **Medium**. Memory spikes; slower time-to-first-byte.        | Stream responses with `iter_bytes()` or `iter_chunks()`.                  |
| `STOR-PERF-003` | Not using signed URLs for direct client uploads     | **Medium**. Backend becomes bottleneck for large files.      | Generate signed URLs; let clients upload directly to GCS/S3.              |
| `STOR-PERF-004` | Missing CDN for static assets                       | **Medium**. Every request goes to origin server.             | Use Cloud CDN, CloudFront, or Vercel Edge for static files.               |

---

## 5. Memory & Resource Management

| ID        | Issue                                 | Impact                                              | Verification Strategy                                                |
| --------- | ------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------- |
| `MEM-001` | Loading large datasets into memory    | **Critical**. OOMKilled errors; container restarts. | Stream data; use generators; paginate reads.                         |
| `MEM-002` | Memory leaks from unclosed resources  | **High**. Memory grows over time; eventual OOM.     | Use context managers (`with`). Audit for unclosed files/connections. |
| `MEM-003` | Container memory too low for workload | **High**. Frequent OOM restarts.                    | Monitor memory usage; increase Cloud Run/Lambda memory allocation.   |
| `MEM-004` | Caching without TTL or size limits    | **Medium**. Cache grows unbounded.                  | Use `@lru_cache(maxsize=N)` or TTL-based caching (Redis).            |

---

## 6. Concurrency & Parallelism

| ID         | Issue                                       | Impact                                           | Verification Strategy                                           |
| ---------- | ------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------- |
| `CONC-001` | Blocking operations in async code           | **High**. Blocks event loop; kills throughput.   | Use `await` for I/O. Run blocking code in `run_in_executor()`.  |
| `CONC-002` | Too high concurrency for memory             | **High**. Multiple requests exhaust memory.      | Lower Cloud Run `--concurrency` to match memory/workload ratio. |
| `CONC-003` | Sequential API calls that could be parallel | **Medium**. Latency = sum instead of max.        | Use `asyncio.gather()` for independent async calls.             |
| `CONC-004` | Global state mutation without locks         | **Medium**. Race conditions and data corruption. | Use `threading.Lock` or avoid shared mutable state.             |

---

## 7. Caching

| ID          | Issue                                        | Impact                                                 | Verification Strategy                                |
| ----------- | -------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------- |
| `CACHE-001` | Repeated identical database queries          | **High**. Unnecessary read costs and latency.          | Implement request-scoped or time-based caching.      |
| `CACHE-002` | Not caching external API responses           | **Medium**. Rate limits and latency on repeated calls. | Cache with TTL based on data freshness requirements. |
| `CACHE-003` | Caching at wrong layer (too granular/coarse) | **Medium**. Low cache hit rate.                        | Measure cache hit rate; adjust granularity.          |

---

## 8. Container & Build Optimization

| ID          | Issue                                           | Impact                                                       | Verification Strategy                                       |
| ----------- | ----------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------- |
| `BUILD-001` | Not using multi-stage Docker builds             | **Medium**. Image includes build tools and dev dependencies. | Separate builder and runtime stages.                        |
| `BUILD-002` | Installing dev dependencies in production image | **Medium**. Larger image; slower cold starts.                | Use `poetry install --only=main` or `pip install --no-dev`. |
| `BUILD-003` | Not leveraging layer caching                    | **Medium**. Full rebuild on every change.                    | Order Dockerfile: deps first, then code.                    |
| `BUILD-004` | Using `latest` tag for base images              | **Low**. Unpredictable builds.                               | Pin specific versions (e.g., `python:3.11-slim`).           |

---

## 9. Logging & Observability Overhead

| ID             | Issue                                | Impact                                          | Verification Strategy                                  |
| -------------- | ------------------------------------ | ----------------------------------------------- | ------------------------------------------------------ |
| `LOG-PERF-001` | Debug-level logging in production    | **Medium**. High log volume; increased latency. | Set log level to INFO or WARNING in production.        |
| `LOG-PERF-002` | Synchronous logging blocking request | **Low-Medium**. Adds latency to each request.   | Use async logging handlers or background log shipping. |
| `LOG-PERF-003` | Tracing every request in production  | **Medium**. Overhead from trace export.         | Sample traces (e.g., 10% of requests) in production.   |

---

## 10. Platform-Specific Efficiency Issues

### Cloud Run

| ID       | Issue                          | Impact                                                   | Verification Strategy                                    |
| -------- | ------------------------------ | -------------------------------------------------------- | -------------------------------------------------------- |
| `CR-001` | CPU throttled between requests | **Medium**. Background tasks don't run.                  | Set `--cpu-throttling=false` for always-on CPU.          |
| `CR-002` | Health check endpoint too slow | **High**. Instances marked unhealthy; traffic disrupted. | Ensure `/health` returns in <200ms with no dependencies. |

### AWS Lambda

| ID           | Issue                                      | Impact                                       | Verification Strategy                              |
| ------------ | ------------------------------------------ | -------------------------------------------- | -------------------------------------------------- |
| `LAMBDA-001` | Package too large (>50MB)                  | **High**. Slow deployment and cold starts.   | Use layers for dependencies; exclude unused files. |
| `LAMBDA-002` | Not reusing connections across invocations | **Medium**. New connections on every invoke. | Declare clients outside handler function.          |

### Vercel / Edge Functions

| ID           | Issue                       | Impact                          | Verification Strategy                  |
| ------------ | --------------------------- | ------------------------------- | -------------------------------------- |
| `VERCEL-001` | Large API route bundle size | **Medium**. Slower cold starts. | Code-split; tree-shake unused imports. |

---

## Quick Audit Commands

```bash
# Check for N+1 query patterns (Firestore)
grep -rn "\.get(" --include="*.py" backend/ | grep -v "get_settings\|get_service"

# Find synchronous HTTP calls in async functions
grep -rn "requests\." --include="*.py" backend/

# Check for missing connection reuse
grep -rn "Client()" --include="*.py" backend/ | grep -v "# reused"

# Find large imports
python -X importtime -c "import backend.main" 2>&1 | sort -t: -k2 -n | tail -20

# Check Docker image size
docker images | grep elevendops
```

---

## Previously Identified & Fixed Issues

| Issue                                | Status      | Location                                                           |
| ------------------------------------ | ----------- | ------------------------------------------------------------------ |
| Temp file I/O for ElevenLabs uploads | ✅ Fixed    | `backend/services/elevenlabs_service.py` → Refactored to `BytesIO` |
| Dev dependencies in prod image       | ✅ Verified | `Dockerfile.cloudrun` uses `--only=main`                           |

---

## References

- [Cloud Run Performance Optimization](https://cloud.google.com/run/docs/tips/performance)
- [AWS Lambda Performance Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Firestore Performance Best Practices](https://firebase.google.com/docs/firestore/best-practices)

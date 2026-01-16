# Docker Image Optimization Plan

**Created**: 2026-01-16  
**Current Size**: 1.59 GB (uncompressed) / ~300-400 MB (compressed on Artifact Registry)  
**Target Size**: ~1.3-1.4 GB (uncompressed) / ~250-300 MB (compressed)

---

## Current Image Breakdown

| Component                      | Size    | Percentage |
| :----------------------------- | :------ | :--------- |
| Python Dependencies (`.venv/`) | 547 MB  | ~34%       |
| Python Runtime (`/usr/`)       | ~183 MB | ~12%       |
| System Libraries               | ~63 MB  | ~4%        |
| Application Code               | ~2 MB   | <1%        |
| Other/Overhead                 | ~795 MB | ~50%       |

---

## Optimization Tasks

### Priority 1: Add `--no-cache` to uv sync

- [ ] Update `Dockerfile` line 36
- **Savings**: 20-50 MB
- **Risk**: None
- **Time**: 1 minute

```dockerfile
# Change:
RUN uv sync --frozen --no-dev --no-install-project

# To:
RUN uv sync --frozen --no-dev --no-install-project --no-cache
```

---

### Priority 2: Audit and Remove Unused Dependencies

- [ ] Review `pyproject.toml` for unused packages
- [ ] Move dev-only tools to `[tool.uv.dev-dependencies]`
- [ ] Test application after removal
- **Savings**: 50-150 MB
- **Risk**: Low (requires testing)
- **Time**: 30 minutes

#### Packages to Review

| Package                        | Question                               |
| :----------------------------- | :------------------------------------- |
| `poetry`                       | Still needed? We use `uv` now.         |
| `langchain-community`          | Is it used, or just `langchain`?       |
| HTTP clients                   | Both `httpx` and `requests`? Pick one. |
| `pytest`, `hypothesis`, `ruff` | Should be in dev dependencies only     |

#### How to Check Unused Imports

```bash
# Find what's actually imported in your code
grep -r "^import\|^from" backend/ streamlit_app/ | cut -d: -f2 | sort -u
```

---

### Priority 3: Implement Multi-Stage Build

- [ ] Create builder stage for dependency installation
- [ ] Create runtime stage with only necessary files
- [ ] Test deployment after changes
- **Savings**: 50-100 MB
- **Risk**: Low
- **Time**: 15 minutes

#### Multi-Stage Dockerfile Template

```dockerfile
# Stage 1: Build
FROM python:3.11-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

# Stage 2: Runtime
FROM python:3.11-slim-bookworm AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser backend/ ./backend/
COPY --chown=appuser:appuser streamlit_app/ ./streamlit_app/
COPY --chown=appuser:appuser scripts/start.sh ./start.sh
RUN chmod +x ./start.sh
USER appuser
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app"
EXPOSE 8080
CMD ["./start.sh"]
```

---

## Not Recommended

### Switch to Alpine Linux

- ❌ **Not recommended** for this project
- Reason: `grpcio` (used by Firestore) has compatibility issues with Alpine's `musl` libc
- Often results in **larger** final images due to needing build tools
- Much longer build times

---

## Verification Commands

```bash
# Build locally
docker build -t elevendops-local:latest -f Dockerfile .

# Check total size
docker images elevendops-local:latest --format "{{.Size}}"

# Check layer breakdown
docker run --rm elevendops-local:latest sh -c "du -sh /app/.venv /app/backend /app/streamlit_app /usr"

# Detailed layer history
docker history elevendops-local:latest
```

---

## Notes

- The 1.59 GB local size vs ~300 MB on Artifact Registry is due to **compression**
- Docker stores images uncompressed locally for fast container startup
- When pushed to a registry, images are compressed with gzip/zstd
- Your application code (~2 MB) is negligible; optimizations should focus on dependencies

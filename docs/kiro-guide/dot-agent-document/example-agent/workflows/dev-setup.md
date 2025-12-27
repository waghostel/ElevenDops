---
description: How to set up the development environment from scratch
---

# Development Setup Workflow

This workflow initializes the development environment for new team members.

## Prerequisites

- Git installed
- Node.js 18+ installed
- Python 3.11+ installed
- Docker Desktop installed (optional, for database)

## Steps

### Step 1: Clone Repository

```powershell
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

### Step 2: Install Node Dependencies

// turbo

```powershell
pnpm install
```

### Step 3: Install Python Dependencies

// turbo

```powershell
uv sync
```

### Step 4: Configure Environment

```powershell
Copy-Item .env.example .env
```

> [!IMPORTANT]
> Edit `.env` and fill in your API keys and configuration values.

### Step 5: Start Database (Optional)

```powershell
docker-compose up -d postgres redis
```

### Step 6: Run Migrations

```powershell
pnpm run db:migrate
```

### Step 7: Verify Setup

// turbo

```powershell
pnpm run dev
```

---

## Environment Variables

| Variable       | Description                  | Required |
| :------------- | :--------------------------- | :------- |
| `DATABASE_URL` | PostgreSQL connection string | Yes      |
| `REDIS_URL`    | Redis connection string      | No       |
| `API_KEY`      | External API key             | Yes      |

---

## IDE Setup

### VS Code Extensions

- ESLint
- Prettier
- Python
- Tailwind CSS IntelliSense

### Recommended Settings

See `.vscode/settings.json` for recommended configuration.

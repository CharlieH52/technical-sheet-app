# Computer Inventory System

> A lightweight, cross-platform hardware inventory tool that collects system specs,
> stores them locally in SQLite, and optionally syncs with a remote MySQL server.
> Designed for silent deployment via PyInstaller.

---

## Features

- **Hardware Scanning** — Automatically collects CPU, motherboard, RAM modules,
  storage, OS, network, and AnyDesk ID.
- **Triple Persistence Layer** — JSON (legacy), SQLite (local), and MySQL (remote).
- **Smart Sync** — Uses MAC address as the unique identifier to update existing
  records or create new ones.
- **Connection Pooling** — MySQL repository uses connection pools for efficient
  remote synchronization.
- **Rich Notifications** — Tkinter popups with automatic error logging for messages
  exceeding 100 characters.
- **Environment-Driven** — All remote settings are controlled via `.env` variables.
- **Silent Execution** — No console output; designed for `--noconsole` PyInstaller builds.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  WMI / System   │────▶│  ComputerBuilder   │────▶│   Computer      │
│   Providers     │     │   (Aggregator)    │     │  (Dataclass)    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                        │
           ┌────────────────────────────────────────────┼────────────┐
           │                                            │            │
           ▼                                            ▼            ▼
  ┌─────────────────┐                          ┌─────────────────┐  ┌─────────────────┐
  │  JSON Legacy    │                          │   SQLite Local │  │  MySQL Remote   │
  │ localStorage.json│                          │  localStorage.db│  │  Remote Server  │
  └─────────────────┘                          └─────────────────┘  └─────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.10+
- MySQL Server 8.0+ (only if using remote sync)

### Clone & Setup

```bash
git clone https://github.com/your-org/computer-inventory.git
cd computer-inventory
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Requirements

```
mysql-connector-python>=8.0.0
python-dotenv>=1.0.0
pyinstaller>=6.0.0   # optional, for building executable
```

---

## Configuration

Create a `.env` file in the project root. All remote and optional settings are controlled
through environment variables.

### Minimal Local-Only Setup

```env
USE_MYSQL_REMOTE=false
```

### Full Setup with Remote MySQL

```env
# ── Remote MySQL Toggle ──────────────────────────────────────
USE_MYSQL_REMOTE=true

# ── Required MySQL Connection ────────────────────────────────
MYSQL_HOST=192.168.1.50
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=SuperSecret123!
MYSQL_DATABASE=computers_inventory

# ── Optional Pool Settings ───────────────────────────────────
MYSQL_POOL_NAME=computer_pool
MYSQL_POOL_SIZE=10

# ── Optional SSL ─────────────────────────────────────────────
MYSQL_SSL_CA=/path/to/ca.pem
MYSQL_SSL_VERIFY_CERT=true
```

> [!NOTE]
> The `USE_MYSQL_REMOTE` variable is the **dedicated switch** for remote synchronization.
> Set it to `true` to enable MySQL sync, or `false` (default) to keep everything local.

> [!IMPORTANT]
> `ComputerRepositoryMySQL` **does not** create the database or tables automatically.
> You must run `schema.sql` on your MySQL server before launching the application.
> See the [Database Setup](#database-setup) section below.

> [!WARNING]
> Never commit your `.env` file to version control. Add it to `.gitignore` immediately.
> The MySQL password and SSL certificates are sensitive credentials.

---

## Database Setup

### MySQL Schema

Run the provided SQL script on your remote MySQL server:

```bash
mysql -u root -p < schema.sql
```

Or from the MySQL client:

```sql
SOURCE /path/to/schema.sql;
```

> [!NOTE]
> The schema creates two InnoDB tables with `utf8mb4` charset:
> - `computers` — master record keyed by MAC address.
> - `dimm_ram` — one-to-many child table for memory modules.
> - Automatic timestamps (`created_at`, `updated_at`) are handled by MySQL.

### SQLite

SQLite is **zero-config**. The database file (`localStorage.db`) is created
automatically in the working directory on first run.

---

## Usage

### Running from Source

```bash
python main.py
```

### Building with PyInstaller (Silent / No Console)

```bash
pyinstaller --onefile --noconsole --name "InventoryAgent" main.py
```

> [!NOTE]
> The `--noconsole` flag is essential. The application uses Tkinter popups for all
> user feedback and writes error logs to `error_logs.txt` instead of stdout.

### What Happens on Execution

1. **Collect** — Gathers hardware, OS, network, user, and AnyDesk data.
2. **Build** — Assembles a `Computer` dataclass with a list of `DimmRam` objects.
3. **Persist JSON** *(legacy)* — Updates `localStorage.json` by MAC address.
4. **Persist SQLite** — Upserts the record into the local SQLite database.
5. **Persist MySQL** *(conditional)* — If `USE_MYSQL_REMOTE=true`, syncs with the remote server.
6. **Notify** — Shows a success popup. Errors are logged automatically.

---

## Project Structure

```
computer-inventory/
├── main.py                                    # Entry point
├── .env                                       # Environment variables (not in git)
├── schema.sql                                 # MySQL DDL script
├── requirements.txt
├── src/
│   ├── computer_builder.py                    # Aggregates system data into Computer
│   ├── models/
│   │   ├── computer.py                        # Computer dataclass
│   │   └── ram.py                             # DimmRam dataclass
│   ├── modules/
│   │   ├── mod_anydesk.py                     # AnyDesk ID provider
│   │   ├── mod_hardware.py                    # CPU, mobo, storage provider
│   │   ├── mod_network.py                     # IP & MAC provider
│   │   ├── mod_os.py                          # OS info provider
│   │   └── mod_user.py                        # Username provider
│   ├── notifications/
│   │   └── popup.py                           # PopUp, PopUpWarning, PopUpError, ErrorLogger
│   └── repository/
│       ├── computer_repository.py             # JSON legacy repository
│       ├── computer_repository_sqlite.py      # SQLite repository
│       └── computer_repository_mysql.py       # MySQL remote repository
```

---

## Notification & Logging System

The `popup.py` module provides four classes:

| Class | Icon | Behavior |
|-------|------|----------|
| `PopUp` | ℹ️ Info | General information messages |
| `PopUpWarning` | ⚠️ Warning | Non-critical alerts (e.g., RAM module count changed) |
| `PopUpError` | ❌ Error | Critical failures (e.g., permission denied, connection lost) |
| `ErrorLogger` | 📝 File | Writes timestamped entries to `error_logs.txt` |

> [!NOTE]
> If a message exceeds **100 characters**, the full text is automatically saved to
> `error_logs.txt` in the working directory, and the user sees a summary popup with
> the file path. This is ideal for PyInstaller `--noconsole` builds where stdout is
> not visible.

### Log Format

```
[2026-08-14 09:15:32]  TÍTULO: Error de Conexión MySQL
[2026-08-14 09:15:32]  MENSAJE:
No se pudo establecer conexión con el servidor MySQL remoto en 192.168.1.50:3306.
============================================================
```

---

## Migrating from JSON to Relational Databases

To stop using raw JSON and migrate fully to SQLite/MySQL:

1. Comment or remove the `[LEGACY-JSON]` blocks in `main.py`.
2. Ensure `ComputerRepositorySQLite` remains active (it is enabled by default).
3. (Optional) Enable remote sync by setting `USE_MYSQL_REMOTE=true` and configuring
   the `MYSQL_*` variables.
4. Delete `localStorage.json` when you no longer need legacy data.

> [!IMPORTANT]
> The JSON repository (`ComputerRepositoryLocal`) is kept for backward compatibility.
> New deployments should rely on SQLite as the primary local store.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_MYSQL_REMOTE` | No | `false` | Master toggle for remote MySQL sync |
| `MYSQL_HOST` | If remote | — | MySQL server hostname or IP |
| `MYSQL_PORT` | No | `3306` | MySQL server port |
| `MYSQL_USER` | If remote | — | Database username |
| `MYSQL_PASSWORD` | If remote | — | Database password |
| `MYSQL_DATABASE` | If remote | — | Database name |
| `MYSQL_POOL_NAME` | No | `computer_pool` | Connection pool identifier |
| `MYSQL_POOL_SIZE` | No | `5` | Number of connections in the pool |
| `MYSQL_CHARSET` | No | `utf8mb4` | Connection charset |
| `MYSQL_SSL_CA` | No | — | Path to CA certificate for SSL |
| `MYSQL_SSL_VERIFY_CERT` | No | `false` | Verify server certificate |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

> [!NOTE]
> Please ensure your code follows the existing docstring style (Spanish for internal
> documentation, English for public-facing README and commit messages).

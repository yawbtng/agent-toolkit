# Portless Command Reference

## Run an App

```
portless run [--name <name>] <cmd> [args...]
portless <name> <cmd> [args...]
```

Infers project name from package.json, git root, or directory name.

**Flags:**
- `--name <name>` — Override inferred base name (worktree prefix still applies)
- `--app-port <number>` — Use fixed port instead of auto-assignment; configurable via `PORTLESS_APP_PORT`
- `--force` — Override existing route registered by another process

**Examples:**
- `portless run next dev` — infer name from project
- `portless run --name myapp next dev` — override inferred name
- `portless myapp next dev` — explicit name shorthand
- `portless api pnpm start` — name a service "api"
- `portless docs.myapp next dev` — subdomain routing

## Get Service URL

```
portless get <name>
```

Print the URL for a service. Useful for wiring services together in scripts or env vars.

```bash
BACKEND_URL=$(portless get backend)
```

Applies worktree prefix detection by default; use `--no-worktree` to skip.

## Alias (Static Routes)

```
portless alias <name> <port>
portless alias <name> <port> --force
portless alias --remove <name>
```

Register a route for a service not managed by portless (e.g., a Docker container). Aliases persist across stale-route cleanup.

**Examples:**
- `portless alias my-postgres 5432` — http://my-postgres.localhost:1355
- `portless alias redis 6379` — http://redis.localhost:1355
- `portless alias --remove my-postgres` — remove the alias

## List Routes

```
portless list
```

Shows active routes and their assigned ports.

## Trust the CA

```
sudo portless trust
```

Adds the portless certificate authority to the system trust store. Required once for HTTPS with auto-generated certs.

## Proxy Control

### Start

```
portless proxy start
```

**Flags:**
- `-p, --port <number>` — Proxy port (default: 1355); below 1024 requires sudo
- `--https` — Enable HTTP/2 + TLS with auto-generated certs
- `--tld <tld>` — Custom TLD instead of `.localhost` (e.g., `test`); auto-syncs `/etc/hosts`
- `--cert <path>` — Custom TLS certificate (implies `--https`)
- `--key <path>` — Custom TLS private key (implies `--https`)
- `--no-tls` — Disable HTTPS (overrides `PORTLESS_HTTPS`)
- `--foreground` — Run in foreground instead of daemon mode

### Stop

```
portless proxy stop
```

## Hosts Management

```
sudo portless hosts sync     # add current routes to /etc/hosts
sudo portless hosts clean    # remove portless entries from /etc/hosts
```

Auto-enabled for custom TLDs. For `.localhost`, set `PORTLESS_SYNC_HOSTS=1` to enable.

## Bypass Portless

```
PORTLESS=0 pnpm dev
```

Runs the command directly without the proxy.

## Configuration (Environment Variables)

| Variable | Purpose | Default |
|----------|---------|---------|
| `PORTLESS_PORT` | Proxy listening port | 1355 |
| `PORTLESS_HTTPS` | Enable HTTPS (set to `1`) | off |
| `PORTLESS_TLD` | Custom TLD replacing `.localhost` | localhost |
| `PORTLESS_APP_PORT` | Fixed app port (disables auto-assignment) | random 4000-4999 |
| `PORTLESS_SYNC_HOSTS` | Auto-sync `/etc/hosts` (set to `1`) | off |
| `PORTLESS_STATE_DIR` | Override state directory location | varies |
| `PORTLESS` | Set to `0` to bypass proxy | enabled |

## State Directory

- Ports <1024 (sudo, macOS/Linux): `/tmp/portless`
- Ports >=1024 (no sudo): `~/.portless`
- Windows: `~/.portless`

**State files:** routes.json, routes.lock, proxy.pid, proxy.port, proxy.log

## Framework Auto-Detection

Portless auto-injects `--port` and `--host` flags for frameworks that don't respect the `PORT` environment variable:
- Vite
- Astro
- React Router
- Angular
- Expo
- React Native

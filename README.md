# Aether

**Modern homelab dashboard** — real-time status, system metrics, and weather in a clean glassmorphism UI.

Served directly at your server IP (port 80). Built for Sadova Network.

## Features

- **Live service monitoring** — HTTP, ping, and TCP checks performed server-side
- **System metrics** — CPU, RAM, disk, temperature, and real-time network traffic graphs
- **Weather widget** — OpenWeather integration
- **Beautiful & fast** — Glassmorphism design, canvas sparklines, Tailwind + vanilla JS
- **Mobile optimized** — Responsive layout that works great on phones
- **Simple deployment** — Docker image built via GitHub Actions, deployed through Portainer

## Quick Start (Production)

### 1. Prepare host configuration

```bash
# On your Docker server
sudo mkdir -p /opt/aether/config
```

Copy your configuration file (use `config/config.yml.example` as template):

```bash
scp config/config.yml user@server:/opt/aether/config/
```

### 2. Deploy via Portainer

**Recommended method:**

1. Go to **Stacks → Add stack**
2. Select **Repository**
3. Repository URL: `https://github.com/Vatsonio/aether`
4. Compose path: `docker-compose.yml`
5. Add Environment variable:
   - `OPENWEATHER_API_KEY` = your key from [openweathermap.org](https://openweathermap.org/api)
6. Deploy

Aether will be available at `http://your-server-ip` (no port needed).

### Environment Variables

| Variable                | Description                          | Default |
|-------------------------|--------------------------------------|---------|
| `OPENWEATHER_API_KEY`   | OpenWeatherMap API key               | —       |
| `WEATHER_DEFAULT_CITY`  | Default city for weather widget      | Kyiv    |

The key from environment variables takes priority over the value in `config.yml`.

### Updating

- Push changes to `main`
- GitHub Actions automatically builds and pushes new image to GHCR
- In Portainer: **Update the stack** or recreate the container

## Local Development

```bash
cd aether
setup.bat          # first run (creates venv + installs)
run.bat            # start development server
```

Open http://localhost:8090

## Configuration

All services and settings are defined in the mounted config file:

`/opt/aether/config/config.yml`

See [config/config.yml.example](config/config.yml.example) for the full structure and supported check types.

## Architecture

```
Frontend (static/index.html)  ← served by FastAPI
          ↓
Backend (FastAPI)             ← /api/status, /api/weather, /api/config
          ↓
Config (host-mounted YAML)    ← services, weather, intervals
```

- Image: `ghcr.io/vatsonio/aether:latest`
- Built automatically on push via `.github/workflows/docker-build.yml`

## Versioning

Versions follow the pattern `V1.N`, where `N` equals the current commit count.

## License

Internal use for Sadova Network.

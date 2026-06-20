"""
Aether - Modern Homelab Dashboard
Autonomous implementation: FastAPI + live server-side health checks + beautiful glass UI
"""

import asyncio
import os
import time
from typing import Literal, Optional, List, Dict, Any
from pathlib import Path

import httpx
import yaml
import socket
import asyncio
import psutil
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# Paths
ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config" / "config.yml"
STATIC_DIR = ROOT / "static"

# Models
StatusType = Literal["up", "down", "unknown"]
CheckType = Literal["http", "ping", "tcp"]


class StatusCheck(BaseModel):
    type: CheckType = "http"
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    interval: int = 30
    timeout: int = 5
    insecure: bool = False
    accept_status: List[int] = Field(default_factory=lambda: [200, 301, 302, 401, 403])


class ServiceItem(BaseModel):
    name: str
    subtitle: str = ""
    url: str
    icon: str = "🔗"
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True
    status: Optional[StatusCheck] = None


class ServiceGroup(BaseModel):
    name: str
    icon: str = "📁"
    items: List[ServiceItem]


class WeatherConfig(BaseModel):
    openweather_api_key: str = ""
    default_city: str = "Kyiv"


class AppConfig(BaseModel):
    title: str = "Aether"
    subtitle: str = "Homelab"
    refresh_interval: int = 30
    timeout: int = 5
    services: List[ServiceGroup]
    weather: WeatherConfig = Field(default_factory=WeatherConfig)

    @field_validator("services")
    @classmethod
    def filter_enabled(cls, v):
        for group in v:
            group.items = [i for i in group.items if i.enabled]
        return v


class ItemStatus(BaseModel):
    name: str
    status: StatusType = "unknown"
    latency_ms: Optional[float] = None
    last_checked: Optional[float] = None
    error: Optional[str] = None


class DashboardStatus(BaseModel):
    items: Dict[str, ItemStatus]
    last_global_check: float


# Health Checker
class HealthEngine:
    def __init__(self, config: AppConfig):
        self.config = config
        self.status_cache: Dict[str, ItemStatus] = {}
        self._lock = asyncio.Lock()
        self._last_check = 0.0

    async def check_http(self, item: ServiceItem, check: StatusCheck) -> ItemStatus:
        start = time.time()
        last_error = None
        for attempt in range(2):  # retry for flaky devices (cameras etc.)
            try:
                async with httpx.AsyncClient(
                    timeout=check.timeout,
                    verify=not check.insecure,
                    follow_redirects=True,
                    headers={"User-Agent": "Aether-HealthCheck/1.0"},
                ) as client:
                    resp = await client.get(check.url or item.url)
                    latency = (time.time() - start) * 1000
                    code = resp.status_code
                    # Any response <500 or in accept list → UP (cameras often return 401/404 but are online)
                    if code < 500 or code in (getattr(check, 'accept_status', []) or []):
                        return ItemStatus(
                            name=item.name,
                            status="up",
                            latency_ms=round(latency, 1),
                            last_checked=time.time(),
                        )
                    else:
                        return ItemStatus(
                            name=item.name,
                            status="down",
                            latency_ms=round(latency, 1),
                            last_checked=time.time(),
                            error=f"HTTP {code}",
                        )
            except Exception as e:
                last_error = str(e)[:80]
                if attempt == 0:
                    await asyncio.sleep(0.3)
        return ItemStatus(
            name=item.name,
            status="down",
            last_checked=time.time(),
            error=last_error or "unreachable",
        )

    async def check_ping(self, item: ServiceItem, check: StatusCheck) -> ItemStatus:
        host = check.host or item.url.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
        start = time.time()
        try:
            # Simple TCP connect check (good enough for homelab reachability)
            port = check.port or 80
            loop = asyncio.get_event_loop()
            def do_ping():
                # Try the configured port + common camera/device ports
                ports_to_try = [port]
                for extra in [80, 554, 443, 8080]:
                    if extra not in ports_to_try:
                        ports_to_try.append(extra)
                for p in ports_to_try:
                    for attempt in range(2):
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(check.timeout)
                        try:
                            s.connect((host, p))
                            s.close()
                            return True
                        except Exception:
                            pass
                return False
            success = await loop.run_in_executor(None, do_ping)
            latency = (time.time() - start) * 1000
            if success:
                return ItemStatus(
                    name=item.name,
                    status="up",
                    latency_ms=round(latency, 1),
                    last_checked=time.time(),
                )
            else:
                return ItemStatus(name=item.name, status="down", last_checked=time.time(), error="unreachable")
        except Exception as e:
            return ItemStatus(name=item.name, status="down", last_checked=time.time(), error=str(e)[:80])

    async def check_item(self, item: ServiceItem) -> ItemStatus:
        if not item.status:
            return ItemStatus(name=item.name, status="unknown")
        if item.status.type == "http":
            return await self.check_http(item, item.status)
        elif item.status.type == "ping":
            return await self.check_ping(item, item.status)
        else:
            return await self.check_http(item, item.status)

    async def run_checks(self):
        async with self._lock:
            tasks = []
            for group in self.config.services:
                for item in group.items:
                    if item.status:
                        tasks.append(self._run_and_cache(item))
            await asyncio.gather(*tasks, return_exceptions=True)
            self._last_check = time.time()

    async def _run_and_cache(self, item: ServiceItem):
        st = await self.check_item(item)
        self.status_cache[item.name] = st

    def get_status(self) -> DashboardStatus:
        return DashboardStatus(
            items=self.status_cache.copy(),
            last_global_check=self._last_check,
        )


# Simple system stats (for mini server panel)
_last_net_counters = None
_last_net_time = None

def get_system_stats():
    global _last_net_counters, _last_net_time

    # CPU
    cpu_percent = psutil.cpu_percent(interval=None)
    logical_cores = psutil.cpu_count(logical=True) or 1
    physical_cores = psutil.cpu_count(logical=False) or logical_cores
    cpu_used_cores = round(cpu_percent / 100 * logical_cores, 1)

    # RAM
    mem = psutil.virtual_memory()

    # Disk (root - assume SSD)
    try:
        disk = psutil.disk_usage('/')
    except Exception:
        disk = None

    # CPU Temp (Linux sensors)
    cpu_temp = None
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name in ['coretemp', 'cpu_thermal', 'k10temp', 'zenpower']:
                if name in temps and temps[name]:
                    cpu_temp = temps[name][0].current
                    break
            if cpu_temp is None:
                # fallback first sensor
                for sensor_list in temps.values():
                    if sensor_list:
                        cpu_temp = sensor_list[0].current
                        break
    except Exception:
        pass

    # Network traffic (current speed)
    net = psutil.net_io_counters()
    up_kbps = 0
    down_kbps = 0
    now = time.time()
    if _last_net_counters is not None and _last_net_time is not None:
        delta = now - _last_net_time
        if delta > 0.08:  # ignore super-frequent calls (noise at 0.5s updates)
            up_kbps = (net.bytes_sent - _last_net_counters.bytes_sent) / delta / 1024
            down_kbps = (net.bytes_recv - _last_net_counters.bytes_recv) / delta / 1024
        else:
            # keep last known rate for smooth display (avoid 0 spikes)
            # we can't easily here without extra globals; will be handled by client history
            pass
    _last_net_counters = net
    _last_net_time = now

    stats = {
        "cpu_percent": round(cpu_percent, 1),
        "cpu_cores": logical_cores,
        "cpu_physical": physical_cores,
        "cpu_used_cores": cpu_used_cores,
        "ram_percent": round(mem.percent, 1),
        "ram_used_gb": round(mem.used / (1024 ** 3), 2),
        "ram_total_gb": round(mem.total / (1024 ** 3), 2),
        "disk_percent": round(disk.percent, 1) if disk else None,
        "disk_free_gb": round(disk.free / (1024 ** 3), 2) if disk else None,
        "disk_total_gb": round(disk.total / (1024 ** 3), 2) if disk else None,
        "cpu_temp": round(cpu_temp, 1) if cpu_temp else None,
        "net_up_kbps": round(up_kbps, 1),
        "net_down_kbps": round(down_kbps, 1),
        "timestamp": now,
    }
    return stats


# Load config
def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = AppConfig(**raw)

    # Override sensitive weather settings from environment variables (recommended for Docker/Portainer)
    env_api_key = os.environ.get("OPENWEATHER_API_KEY")
    if env_api_key:
        cfg.weather.openweather_api_key = env_api_key.strip()

    env_default_city = os.environ.get("WEATHER_DEFAULT_CITY") or os.environ.get("OPENWEATHER_DEFAULT_CITY")
    if env_default_city:
        cfg.weather.default_city = env_default_city.strip()

    return cfg


# App
# Version is managed manually per commit rules (see README)
# Format: V<generation>.<commit_count>
APP_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
app = FastAPI(title="Aether", version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
engine = HealthEngine(config)

# Background health loop
@app.on_event("startup")
async def startup():
    # Initial checks
    await engine.run_checks()
    asyncio.create_task(periodic_checks())


async def periodic_checks():
    while True:
        await asyncio.sleep(max(10, config.refresh_interval))
        await engine.run_checks()


# API
@app.get("/api/config")
async def get_config():
    cfg = config.model_dump()
    # Never expose the real API key to the frontend
    if "weather" in cfg and isinstance(cfg["weather"], dict):
        if "openweather_api_key" in cfg["weather"]:
            key = cfg["weather"]["openweather_api_key"]
            cfg["weather"]["openweather_api_key"] = "***" if key else ""
    return cfg


@app.get("/api/status")
async def get_status():
    return engine.get_status().model_dump()


@app.post("/api/refresh")
async def force_refresh():
    await engine.run_checks()
    return {"ok": True, "checked_at": engine._last_check}


@app.get("/api/weather")
async def get_weather(city: str = None):
    wcfg = getattr(config, 'weather', None) or WeatherConfig()
    api_key = wcfg.openweather_api_key
    default_city = wcfg.default_city or "Kyiv"

    city = city or default_city

    if not api_key:
        return {"error": "OpenWeather API key is not configured (set OPENWEATHER_API_KEY env or in config.yml)"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": api_key,
                    "units": "metric",
                    "lang": "uk"
                }
            )
            data = resp.json()

            if resp.status_code != 200:
                return {"error": data.get("message", "Failed to fetch weather")}

            return {
                "city": data.get("name", city),
                "temp": round(data["main"]["temp"]),
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
            }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/system")
async def get_system():
    return get_system_stats()


@app.get("/api/version")
async def get_version():
    return {"version": APP_VERSION}


# Serve beautiful frontend (glassmorphism)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content)
    return HTMLResponse("<h1>Aether running. static/index.html missing</h1>")


# Health for container
@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8090"))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)

# Aether

Сучасний homelab дашборд для Sadova Network.

Створено **автономно** з нуля у окремій папці.

## Особливості (обрана архітектура)

- **Backend**: FastAPI + Python - серверні health checks (http + ping)
- **Frontend**: Чиста сучасна SPA (Tailwind + vanilla JS) - дуже легка та швидка
- **Конфіг**: Звичний YAML (схожий на Homer / Homepage)
- **Статуси в реальному часі**: Пінг + HTTP запити виконуються на сервері (не ламається CORS)
- **Стиль**: Glassmorphism + OLED dark з акцентом #38bdf8 (розвинено з оригінального custom.css)
- **Українською** за замовчуванням

## Запуск (Windows)

### Найпростіший спосіб

1. **Перший запуск (налаштування):**
   ```bat
   setup.bat
   ```

2. **Звичайні тестові запуски:**
   ```bat
   run.bat
   ```

   Скрипт автоматично:
   - Створює `venv`, якщо його немає
   - Активує віртуальне оточення
   - Встановлює залежності (тільки при першому запуску)
   - Запускає Aether на `http://localhost:8090` (локальна розробка)

### Ручний запуск (PowerShell)

```powershell
cd aether
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Відкрий у браузері: **http://localhost:8090** (для локальної розробки)

**У Docker / на сервері** - Aether відкривається просто на IP без порту: `http://192.168.31.5` (порт 80).

### Docker

```bash
docker compose up --build -d
```

Після запуску дашборд буде доступний на **http://<твій-ip>** (порт 80 без вказання порту).

Для локального запуску (run.bat / run.py) - порт **8090**.

### CI/CD + Розгортання через Portainer (правильний спосіб)

**Логіка:**
- GitHub Actions автоматично збирає Docker-образ і пушить в `ghcr.io/vatsonio/aether`
- Portainer просто тягне готовий образ (не збирає сам)

#### Крок 1: Підготовка конфігу на сервері

Створи на Docker-хості директорію для конфігу:

```bash
ssh user@192.168.31.5
sudo mkdir -p /opt/aether/config
```

Скопіюй свій реальний `config/config.yml` (з усіма сервісами) на сервер:

```powershell
# з Windows
scp "C:\Users\VATS\Documents\Proj\Homer config\aether\config\config.yml" user@192.168.31.5:/opt/aether/config/
```

(або скопіюй `config.yml.example` як основу і відредагуй).

#### Крок 2: GitHub Actions (збирає образ)

Коли запушитиш зміни в `main` (або натиснеш **Run workflow** вручну в GitHub):

- `.github/workflows/docker-build.yml` збере образ
- Запушить теги: `latest` + `V1.x` (з файлу `VERSION`)

Перевірити білд можна тут:  
https://github.com/Vatsonio/aether/actions

#### Крок 3: Деплой через Portainer (рекомендовано)

Найкращий і найпростіший спосіб:

1. У Portainer зайди в **Stacks** → **Add stack**
2. Вибери **"Repository"** (не Web editor!)
3. Repository: `https://github.com/Vatsonio/aether`
4. Reference: `refs/heads/main` (або main)
5. Compose path: `docker-compose.yml`
6. Назва стеку: `aether`
7. **Deploy the stack**

Portainer сам склонирує репо, візьме compose (який використовує готовий образ з GHCR), потягне image і запустить.

Після цього Aether буде на **http://192.168.31.5** (порт 80).

#### Альтернатива (Web editor)

Можна просто вставити вміст `docker-compose.yml` з репозиторію — образ теж підтягнеться автоматично (бо там `image:`, а не `build:`).

**Важливо:**
- Порт 80 має бути вільним.
- Config монтується з `/opt/aether/config` на хості.
- Якщо хочеш нову версію — запусти workflow або запуш коміт → image оновиться → в Portainer на контейнері **Recreate** / Update stack.

#### Локальна розробка

Залишилось без змін: `run.bat` або `python run.py` → http://localhost:8090

Для локального Docker білду (тимчасово):
```bash
# додай на час в compose: build: .
docker compose build
docker compose up -d
```

## Конфігурація

Редагуй `config/config.yml`.

Підтримувані типи перевірок:

```yaml
status:
  type: http          # або ping
  url: http://...
  interval: 30
  timeout: 5
  insecure: true      # для self-signed
  accept_status: [200, 301, 302, 401]
```

## Переваги над оригінальним Homer

- Статуси обчислюються на сервері (краще для внутрішньої мережі)
- Показує latency (мс)
- Миттєве оновлення без перезавантаження сторінки
- Легко розширюється (FastAPI)

## Troubleshooting (Windows install)

If you see errors like:
- "No space left on device" during `pydantic-core` or maturin
- "Cache entry deserialization failed"

Fixes:
1. Free up space on your main drive (C:).
2. Delete the `venv` folder completely.
3. Run `pip cache purge` (after activating any venv or globally).
4. Re-run `setup.bat`.

The `setup.bat` now uses `--only-binary :all:` to prefer prebuilt wheels and fail fast.

## Структура

```
aether/
├── backend/app.py       # FastAPI + health engine
├── config/config.yml    # Ваша конфігурація
├── static/index.html    # Красивий фронтенд
├── Dockerfile
└── docker-compose.yml
```

Зроблено автономно. Архітектура, стек і дизайн обрані самостійно на основі сучасних практик 2026 (Homepage + FastAPI+Svelte патерни, але спрощено до production-ready легкого рішення без важкої Node збірки).

## Правила комітів та версіонування

**Головне правило:**  
У повідомленнях комітів **заборонена будь-яка AI-атрибуція**.  
Не додавати:
- `Co-Authored-By: ...`
- `Generated with Claude / Grok / ...`
- `Assisted by AI`
- будь-які інші згадки інструментів ШІ

**Формат версій:** `V<generation>.<commit_count>`

- `<generation>` - глобальна версія / "покоління" архітектури (змінюється тільки при великих редизайнах).
- `<commit_count>` - порядковий номер коміту в межах поточного покоління.

Кожен новий коміт → версія зростає (другий номер +1).

Версія вказується:
- у `aether/VERSION`
- у `backend/app.py` (FastAPI)
- у футері дашборду (опціонально)

Перед комітом завжди оновлюй версію.

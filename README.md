# Aether

Сучасний homelab дашборд для Sadova Network.

Створено **автономно** з нуля у окремій папці.

## Особливості (обрана архітектура)

- **Backend**: FastAPI + Python — серверні health checks (http + ping)
- **Frontend**: Чиста сучасна SPA (Tailwind + vanilla JS) — дуже легка та швидка
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
   - Запускає Aether на `http://localhost:8090`

### Ручний запуск (PowerShell)

```powershell
cd aether
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Відкрий у браузері: **http://localhost:8090**

### Docker

```bash
docker compose up --build -d
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

- `<generation>` — глобальна версія / "покоління" архітектури (змінюється тільки при великих редизайнах).
- `<commit_count>` — порядковий номер коміту в межах поточного покоління.

Кожен новий коміт → версія зростає (другий номер +1).

Версія вказується:
- у `aether/VERSION`
- у `backend/app.py` (FastAPI)
- у футері дашборду (опціонально)

Перед комітом завжди оновлюй версію.

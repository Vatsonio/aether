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

**Для погоди:** у Portainer при створенні/редагуванні стеку додай Environment variable:
- `OPENWEATHER_API_KEY` = твій ключ з openweathermap.org

#### Альтернатива (Web editor) — рекомендую якщо "Repository" падає

1. У Portainer: **Stacks → Add stack**
2. Вибери **"Web editor"**
3. Встав **чистий** вміст з файлу `docker-compose.yml` (скопіюй з GitHub → Raw)
4. Назва: `aether`
5. Deploy

Це часто вирішує проблеми з парсингом при використанні Repository.

**Важливо:**
- Порт 80 має бути вільним на хості.
- На сервері **обов'язково** має бути `/opt/aether/config/config.yml`
- Якщо хочеш нову версію — запусти workflow → потім в Portainer **Update the stack** або Recreate контейнер.

#### Якщо помилка: "services must be a mapping"

Це означає, що Portainer не зміг правильно розпарсити файл.

Що робити:

1. **Використовуй Web editor** замість Repository (див. вище) — найшвидше рішення.
2. Переконайся, що в полі **Compose path** (якщо Repository) написано точно:
   `docker-compose.yml`
   (без слешів спереду, без папок).
3. Переконайся, що ти деплоїш з гілки `main`.
4. Скопіюй compose **з Raw** посилання на GitHub, а не з веб-сторінки (щоб не зловити markdown).
5. Видали старий стек повністю і створи новий.
6. Перевір, що останній push пройшов і workflow успішно зібрав образ.

Якщо і це не допоможе — в Portainer при створенні стеку є можливість подивитись preview або логи парсингу.

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

### OpenWeather API ключ (погода)

Рекомендовано передавати ключ через **environment variable** (не в config.yml):

- `OPENWEATHER_API_KEY` — твій API ключ
- `WEATHER_DEFAULT_CITY` (опціонально) — місто за замовчуванням

У docker-compose / Portainer:

```yaml
environment:
  - OPENWEATHER_API_KEY=твій_ключ
```

Ключ з env var має пріоритет над значенням у `config.yml`.

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
├── backend/app.py             # FastAPI + health engine
├── config/config.yml.example  # Шаблон (реальний config.yml тримайте на хості)
├── static/index.html          # Красивий фронтенд
├── Dockerfile
└── docker-compose.yml
```

Реальний `config/config.yml` лежить на хості (`/opt/aether/config/config.yml`) і монтується через volume.


In current code, AppConfig has default for weather.

But if user has minimal yaml without weather, `AppConfig(**raw)` should use default.

Good.

In the override, we always set on cfg.weather which exists.

Now, update the example config weather comment more cleanly (I already did).

One issue: in frontend, the settings might try to show the key? No, from earlier grep, the weather settings only has city input.

See:

In index.html there is settings for weather city, but no key input (good, since key is server-side).

Perfect.

In `/api/config` we now mask the key, so even if someone inspects, it's hidden.

Good.

Now, also update the docker-compose in the repo (already did).

Since user uses Portainer, in the stack they can add environment variables easily.

Finally, since we made changes, we should commit? But according to rules, user controls push, but since this is continuation, I'll make the code changes.

The task is to complete the request by editing code.

Also, perhaps support the key in the YAML still as fallback.

Yes, we did.

I think this is sufficient.

One more: in load_config, the default_factory for weather is used only if not present in raw.

But when we do AppConfig(**raw), if 'weather' not in raw, it uses the default.

Then we override.

Good.

If yaml has weather with empty key, env will override.

Perfect.

Now, to make it even better, perhaps allow env to work even without full config, but no need.

Let's also update the frontend error handling or comments? Not critical.

To test locally, but since no key, and on Windows, I can check syntax.

Now, write the changes.

I think we need to also handle if someone puts the key in the yaml and uses env.

Yes.

Finally, since the compose is now using env comment, user in Portainer can set:

In the stack environment variables: OPENWEATHER_API_KEY = theirkey

Then in compose it's not hardcoded.

In our compose we have it commented.

Perfect.

Also, update the config loading to import? os is already there.

Good.

One small fix: in the override, we should do it after model creation.

Yes.

Also, perhaps make weather always present.

Good.

Now, since the user might have the old config mounted, it will still work (env will take precedence).

Perfect.

I should also check if there are other places using the key.

No.

To complete, perhaps update the docker-compose comment better.

Current edit is okay.

Let's also make sure the compose has the env properly documented.

I think we're good.

Now, since this is code change, and to match previous, perhaps run a quick validation.

But to answer, the code changes are done.

The response should explain to the user how to use it now.

Since the query is to "make it", I edit the files.

Also, update the version? No, follow rules, but since no explicit commit, just edit.

The system allows edits.

One improvement: make the env var override also work if the yaml doesn't have weather section at all.

In current:

If no weather in yaml, raw = {... without weather}, AppConfig will create default WeatherConfig(), then we override the key if env set. Good.

Perfect.

Now, provide clear instructions in response.

Also, update the example more if needed.

I already edited it.

Let me check the current example.```

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

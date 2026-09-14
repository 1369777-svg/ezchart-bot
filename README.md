<div align="center">

# 📊 EZChart

**Screenshot-to-Analysis AI assistant for beginner traders — inside Telegram.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0)](https://docs.aiogram.dev)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?logo=google)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Zero-Cost](https://img.shields.io/badge/Deploy-%240%2Fmonth-success)](docs/DEPLOYMENT.md)

[Features](#-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Roadmap](docs/ROADMAP.md) • [Docs](docs/)

</div>

---

## 🎯 What is EZChart?

EZChart — это Telegram-бот, который за **5 секунд** превращает скриншот графика в понятный технический разбор: тренд, ключевые уровни, Risk/Reward и обучающее объяснение **почему** AI пришёл к такому выводу.

Создан для **начинающих трейдеров**, которым нужен быстрый «второй взгляд» на график без подписки на $50/мес сервисы.

> ⚠️ **Дисклеймер:** EZChart — образовательный инструмент. Он не даёт инвестиционных советов и не является финансовым консультантом.

---

## ✨ Features

| | Feature | Status |
|---|---------|--------|
| 📸 | Анализ скриншота графика (Vision AI) | ✅ MVP |
| 📈 | Определение тренда + силы тренда | ✅ MVP |
| 🎯 | Ключевые уровни поддержки/сопротивления | ✅ MVP |
| ⚖️ | Risk/Reward сценарий с примерным SL/TP | ✅ MVP |
| 🧠 | Anti-Hallucination Engine (защита от выдуманных цен) | ✅ MVP |
| 🎓 | Обучающие объяснения («почему уровень важен») | ✅ MVP |
| 💼 | Paper Trading — виртуальный портфель | 🚧 Phase 2 |
| 📓 | Дневник трейдера с аналитикой | 🚧 Phase 2 |
| 🔌 | Смена AI-провайдера (Gemini / OpenAI / Local) | 🚧 Phase 3 |

---

## 🎬 Demo

**Пример результата:**

```
📊 ОБЩАЯ КАРТИНА
Восходящий тренд на BTC/USDT, 4H таймфрейм.

📈 ТРЕНД
• Направление: восходящий
• Сила: умеренный
• Объяснение: цена делает higher highs и higher lows,
  но momentum замедляется у сопротивления.

🎯 КЛЮЧЕВЫЕ УРОВНИ
• Поддержка: ≈ $67,200 (три отскока)
• Сопротивление: ≈ $69,800 (локальный максимум)

⚖️ RISK / REWARD
• Потенциальный вход: $67,500
• Stop Loss: $66,900 (-0.9%)
• Take Profit: $69,700 (+3.2%)
• Соотношение R/R: 3.5:1

⚠️ ДИСКЛЕЙМЕР
Это образовательный анализ, не финансовая рекомендация.
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram-аккаунт
- Google AI Studio аккаунт (бесплатно)

### 1️⃣ Клонирование
```bash
git clone https://github.com/1369777-svg/ezchart-bot.git
cd ezchart-bot
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Получение ключей

**Telegram Bot Token** → [@BotFather](https://t.me/BotFather) → `/newbot`
**Gemini API Key** → [aistudio.google.com](https://aistudio.google.com) → *Get API key* (без карты)

### 3️⃣ Конфигурация
```bash
cp .env.example .env
# Открой .env и вставь свои ключи
```

### 4️⃣ Запуск
```bash
python -m src.main
```

Открой бота в Telegram → `/start` → отправь скриншот графика. Готово.

---

## 🏗 Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Telegram   │───▶│  aiogram 3   │───▶│  Handlers    │
│    Client    │    │  Dispatcher  │    │  (routing)   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                                │
                            ┌───────────────────┼───────────────────┐
                            ▼                   ▼                   ▼
                    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                    │ Middlewares  │    │  AI Service  │    │  Utilities   │
                    │ (throttling) │    │  (pluggable) │    │  (image)     │
                    └──────────────┘    └──────┬───────┘    └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │  Gemini API  │
                                        │  (Vision)    │
                                        └──────────────┘
```

**Принципы:**
- **Pluggable AI** — `AIClient` абстракция, легко менять провайдера
- **Separation of concerns** — хендлеры не знают про Gemini, сервис не знает про Telegram
- **Anti-hallucination** — промпт + валидация на уровне сервиса
- **Fail-safe** — глобальный error handler + graceful degradation

📖 Подробнее в [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🛠 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Bot Framework | **aiogram 3.x** | Async, typed, production-ready |
| AI Engine | **Google Gemini 2.0 Flash** | Free tier, fast, multimodal |
| Image Processing | **Pillow** | Lightweight, battle-tested |
| Config | **pydantic-settings** | Type-safe env vars |
| Logging | **structlog** | Structured logs для observability |
| Testing | **pytest + pytest-asyncio** | Async-aware |
| Linting | **ruff** | Fast, all-in-one |
| CI/CD | **GitHub Actions** | Free для public repos |
| Hosting | **Render / Oracle Cloud** | Zero-Cost |

---

## 📂 Project Structure

```
ezchart-bot/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Settings
│   ├── handlers/            # Telegram handlers
│   ├── services/            # Business logic (AI, prompts)
│   ├── middlewares/         # Throttling, errors
│   └── utils/               # Helpers
├── tests/                   # Pytest suite
├── docs/                    # Architecture, roadmap, deployment
└── .github/                 # CI, issue templates
```

---

## 🗺 Roadmap

### ✅ Phase 1 — MVP (current)
- Screenshot → AI analysis
- Anti-hallucination prompt
- Zero-cost deploy

### 🚧 Phase 2 — Engagement
- Paper Trading (виртуальный портфель)
- Trade Journal (история + статистика)
- Push-уведомления о срабатывании уровней

### 🔮 Phase 3 — Ecosystem
- Multi-provider AI (OpenAI, Claude, local LLaMA)
- Integration with exchanges (Bybit testnet)
- Community signals (opt-in sharing)

📖 Full roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)

---

## 🧪 Development

```bash
# Install dev deps
pip install -r requirements-dev.txt

# Run tests
pytest

# Lint
ruff check src/

# Format
ruff format src/

# Run locally
python -m src.main
```

---

## 🚢 Deployment

| Platform | Cost | Cold Start | Best for |
|----------|------|-----------|----------|
| **Render** | $0 | 15 min sleep | Quick MVP |
| **Oracle Cloud** | $0 forever | None | Production |
| **Docker (VPS)** | varies | None | Full control |

📖 Пошаговая инструкция: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🤝 Contributing

Мы приветствуем вклад! Смотри [CONTRIBUTING.md](CONTRIBUTING.md).

- 🐛 [Report a bug](https://github.com/1369777-svg/ezchart-bot/issues/new?template=bug_report.md)
- 💡 [Request a feature](https://github.com/1369777-svg/ezchart-bot/issues/new?template=feature_request.md)
- 🔀 [Submit a PR](https://github.com/1369777-svg/ezchart-bot/pulls)

---

## 🔒 Security

Нашёл уязвимость? Смотри [SECURITY.md](SECURITY.md). Не открывай публичный issue.

---

## 📜 License

MIT License — см. [LICENSE](LICENSE).

---

<div align="center">

**⭐ Если проект полезен — поставь звезду!**

Made with love for beginner traders

</div>
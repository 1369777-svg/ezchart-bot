# Architecture

## High-Level Overview

EZChart is a layered app with clear separation of concerns.

Flow:

1. Telegram Client
2. Dispatcher + Routers (commands, language, screenshot)
3. Middlewares (i18n, error handler, throttling)
4. Services (ai_client, prompts)
5. Google Gemini API (Vision)

## Routers

- **commands** — /start, /help, /about
- **language** — /language with inline keyboard
- **screenshot** — main photo analysis pipeline

## Middlewares (in order)

1. **i18n** — resolves user locale (FSM -> Telegram language_code)
2. **ErrorHandler** — global try/except
3. **Throttling** — 1 message / 10 sec per user

## Services

- **ai_client** — Gemini Vision wrapper with fallback chain
- **prompts** — 3 vision prompts (ru / en / it)

## Design Principles

### 1. Pluggable AI Layer
All AI calls go through `analyze_chart()` in `src/services/ai_client.py`.
Swapping the provider (OpenAI, Claude, Groq) doesn't touch handlers.

### 2. Anti-Hallucination Strategy
Three layers of defense:
1. Prompt-level rules: "never invent exact prices"
2. Response validation for ERROR marker
3. UX wording: "visually at ~X", "could not read exact price"

### 3. Multilingual by Design
Two levels:
- UI via aiogram-i18n + .ftl files in locales/
- AI responses via 3 prompt variants

Locale is persisted in FSM state and auto-detected from Telegram language_code.

### 4. Fail-Safe Design
- Global error handler catches everything
- User always gets a meaningful response
- Model fallback: gemini-3.6-flash -> 3 alternatives
- 60-second timeout

### 5. Zero-Cost by Design
- Polling instead of webhook
- Stateless — runs on any free tier
- In-memory FSM — no DB at MVP
- Gemini free tier — 1500 requests/day

## Data Flow

1. User sends photo
2. Telegram Servers forward to aiogram
3. Bot downloads via get_file()
4. Validates with is_supported_image()
5. Calls Gemini Vision in a thread
6. Strips markdown fences from response
7. Splits if > 4000 chars
8. Sends back to user

## Project Structure

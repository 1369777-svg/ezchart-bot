# Roadmap

## Phase 1 — MVP (current)

**Goal:** Validate that beginners get real value from AI chart analysis.

- [x] Telegram bot on aiogram 3.x
- [x] Vision analysis via Gemini 3.6 Flash
- [x] Anti-hallucination prompt engineering
- [x] Multilingual support (ru / en / it)
- [x] Zero-cost deployment
- [ ] First 100 users
- [ ] In-bot NPS survey

**Success metric:** 60% of users return within a week.

## Phase 2 — Engagement (Month 2-3)

### Paper Trading
Virtual portfolio starting at $10,000. User enters trades based on bot signals,
bot tracks P&L via public APIs, auto-closes on SL/TP.

### Trade Journal
History of all analyses and outcomes, win rate stats, CSV export.

### Push Notifications
Alerts when key levels are touched, daily market digest.

**Success metric:** 30% of MAU use Paper Trading.

## Phase 3 — Ecosystem (Month 4-6)

### Multi-Provider AI
Fallback chain: Gemini -> OpenAI -> Groq. Auto-routing by chart type.

### Exchange Integration (testnet first)
Bybit demo API -> real trades on opt-in.

### Community Layer
Opt-in signal sharing, leaderboard, weekly breakdowns.

### Monetization (only if Phase 2 succeeds)
- Free: 5 analyses/day
- Pro ($5/mo): unlimited + Paper Trading + Journal

## Anti-roadmap — what we DON'T do

- Real trading signals ("buy now")
- Profit guarantees
- Managing real user funds (in MVP)
- Owning exchange infrastructure
- A mobile app (Telegram is our UI)
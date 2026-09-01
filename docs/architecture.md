# Architecture notes for TG-Monitoring

## User flow

1. Visitor reads about the service on `/` and `/services`
2. On `/preview` they enter a search query
3. Backend logs into brandanalytics.ru via Playwright, runs the query, parses results
4. Frontend shows mention cards before access purchase
5. User submits an access request with contact details

## brandanalytics.ru automation

Located in `apps/api/app/services/br_analytics/`:

| Module | Responsibility |
|---|---|
| `auth.py` | Login at `/account/login/` (`#username`, `#ba_password`, `#button_submit`) |
| `topics.py` | Opens measurement theme editor, or «Добавить новую тему» if it was removed |
| `search.py` | Fill `#key_words_operator`, click `#show_result_btn` |
| `parser.py` | Parse `#messages_container .feed_item` into `MentionItem` |
| `client.py` | Orchestrates the full preview pipeline |

### Measurement theme (preview searches)

- Name: `Энергострой`
- ID: `14166164`
- Edit URL: `/action/update_theme/14166164/`
- Config: `BR_ANALYTICS_FALLBACK_THEME_ID` / `BR_ANALYTICS_FALLBACK_THEME_NAME`

### Result DOM (from saved `edit_theme.html`)

- Container: `#search_content` → `#messages_container`
- Item: `.feed_item`
- Text: `.msg_text`
- Source link: `a.js--source_link`
- Author: `a.author_name`
- Date: `.msg_date` (`dd.mm.yyyy HH:MM`)

## Planned phases

- Phase 1: Landing + preview API stub
- Phase 2: Working Playwright integration with brandanalytics.ru (current)
- Phase 3: Access request storage + admin notifications
- Phase 4: Telegram bot for continuous mention delivery

## Security

- brandanalytics credentials only in `apps/api/.env` (gitignored)
- Never expose Playwright session to the browser client
- Rate-limit `/preview/search` to prevent abuse

"""Normalize user search queries to Brand Analytics query language via AITUNNEL."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

BA_QUERY_RULES = """
Язык поисковых запросов Brand Analytics:

- Слова по умолчанию ищутся со всеми морфологическими формами.
- Поиск без учёта регистра (кроме оператора "слово"!).

Что учитывается при поиске:
- юникод-буквы (именно буквы, не любые символы), цифры, #, дефис - (не тире);
- при поиске без морфологии (в кавычках) дополнительно: %, #, @, $, ©, №, +.

Операторы:
1) пробел = И (все слова в одном документе): футбол ЦСКА
2) запятая = ИЛИ: футбол, ЦСКА
3) минус = исключение: футбол -ЦСКА -Динамо
4) "фраза"~N = расстояние N слов (N=0..10), морфология сохраняется: "футбол ЦСКА"~5
5) "фраза" = точное соответствие без морфологии: "Банк Москвы"
6) * = начало слова (минимум 3 символа до *; одна * в словосочетании; нельзя с ~, точными кавычками, группировкой, "!): сбербанк*
7) (a, b)*(c, d) = группировка (внутри только И/ИЛИ)
8) (a, b)/N(c, d) = расстояние между группами
9) "IT"! = с учётом регистра

Скобки:
- операторы «Скобки» и «Скобки с расстоянием» допускают вложение скобок в скобки;
- уровней вложения не больше 5;
- пример: ((мороженое, пломбир)/7(стаканчик, эскимо))*(ванильный, шоколадный).

Цель: сделать запрос валидным и эффективным для мониторинга бренда/персоны/события.
""".strip()


SYSTEM_PROMPT = f"""Ты помощник по языку поисковых запросов Brand Analytics.
{BA_QUERY_RULES}

Задача: проверить пользовательский запрос и при необходимости исправить его под правила BA.
- Если запрос уже корректен для BA (есть операторы/кавычки/~N и т.п.) — верни его почти без изменений.
- Если пользователь написал обычный текст без операторов BA (название бренда, ФИО, событие) — обязательно оформи как BA-запрос.
  Типичные шаблоны:
  - бренд/компания: "Название Бренда", НазваниеБренда, brandname
  - персона / ФИО: "Имя Фамилия"~1, "ИмяФамилия"
  - несколько вариантов через запятую (ИЛИ)
- Не оставляй «голый» текст из 1–4 слов без операторов, если это имя/бренд/название.
- Не добавляй лишних минус-слов без явной просьбы пользователя.
- Не выдумывай сущности, которых нет во входном тексте.
- Ответ строго JSON без markdown:
{{"query":"...","changed":true/false,"note":"кратко по-русски что сделано или пустая строка"}}
"""


@dataclass(frozen=True)
class QueryRewriteResult:
    original_query: str
    query: str
    changed: bool
    note: str = ""


class QueryRewriteService:
    async def rewrite(self, query: str) -> QueryRewriteResult:
        original = query.strip()
        if not original:
            return QueryRewriteResult(original_query=query, query=query, changed=False)

        if not settings.aitunnel_configured:
            logger.warning("AITUNNEL not configured; skipping query rewrite")
            return QueryRewriteResult(original_query=original, query=original, changed=False)

        try:
            rewritten = await self._call_llm(original)
        except Exception:  # noqa: BLE001
            logger.exception("Query rewrite failed; using original query")
            return QueryRewriteResult(original_query=original, query=original, changed=False)

        normalized = self._sanitize(rewritten.query) or original
        changed = normalized != original or rewritten.changed
        return QueryRewriteResult(
            original_query=original,
            query=normalized,
            changed=changed and normalized != original,
            note=rewritten.note.strip(),
        )

    async def _call_llm(self, query: str) -> QueryRewriteResult:
        payload = {
            "model": settings.aitunnel_model,
            "max_tokens": settings.aitunnel_max_tokens,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Исходный запрос пользователя:\n{query}\n\nВерни JSON.",
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {settings.aitunnel_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{settings.aitunnel_base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        parsed = self._parse_json_content(content)
        out_query = str(parsed.get("query") or query).strip()
        note = str(parsed.get("note") or "").strip()
        changed = bool(parsed.get("changed")) if "changed" in parsed else out_query != query
        return QueryRewriteResult(
            original_query=query,
            query=out_query,
            changed=changed,
            note=note,
        )

    def _parse_json_content(self, content: str) -> dict:
        text = (content or "").strip()
        if not text:
            return {}
        # Strip optional markdown fences
        fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
        if fenced:
            text = fenced.group(1).strip()
        try:
            data = json.loads(text)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                return {"query": text, "changed": True, "note": ""}
            try:
                data = json.loads(match.group(0))
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                return {"query": text, "changed": True, "note": ""}

    def _sanitize(self, query: str) -> str:
        cleaned = " ".join(query.split())
        return cleaned[:500]

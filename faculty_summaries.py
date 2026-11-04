"""Create source-linked faculty analyses for the published news feed."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import requests

import config
from faculty_db import FacultyDatabase


class FacultySummaryWriter:
    """Assign each item to its best-matched faculty member and summarize it."""

    def __init__(self, session: Any = None):
        self.db = FacultyDatabase()
        self.faculty = self.db.get_faculty_profiles()
        self.session = session if session is not None else requests
        function_name = os.getenv("FACULTY_SUMMARY_FUNCTION", "ask-faculty-voice")
        base_url = config.SUPABASE_URL.rstrip("/")
        self.function_url = (
            f"{base_url}/functions/v1/{function_name}" if base_url and function_name else ""
        )

    def select_author(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Choose the faculty profile with the greatest topical overlap."""
        already_matched = article.get("metadata", {}).get("interested_faculty", [])
        by_slug = {faculty.get("slug"): faculty for faculty in self.faculty}
        for match in already_matched:
            faculty = by_slug.get(match.get("slug"))
            if faculty:
                return faculty

        article_text = " ".join(
            [article.get("title", ""), article.get("description", "")]
        ).lower()
        scored = []
        for faculty in self.faculty:
            topics = faculty.get("news_topics") or []
            score = sum(topic.lower() in article_text for topic in topics)
            if score:
                scored.append((score, faculty))
        return max(scored, key=lambda pair: pair[0])[1] if scored else None

    @staticmethod
    def source_record(article: Dict[str, Any]) -> List[Dict[str, str]]:
        """Make the original reporting explicit in the feed data."""
        url = article.get("url", "")
        if not url:
            return []
        return [{
            "title": article.get("title", "Primary source"),
            "publisher": article.get("source", "Source"),
            "url": url,
        }]

    @staticmethod
    def fallback_summary(article: Dict[str, Any]) -> str:
        """Keep the feed publishable if an AI response is unavailable."""
        description = article.get("description", "").strip()
        if description:
            return description
        return "The source has been selected for its relevance to the Institute's faculty interests."

    def write_summary(self, article: Dict[str, Any], faculty: Dict[str, Any]) -> str:
        """Use Castalia's protected Edge Function, where the Gemini key is stored."""
        if not self.function_url or not config.SUPABASE_KEY:
            return self.fallback_summary(article)

        source_material = {
            "title": article.get("title", ""),
            "publisher": article.get("source", ""),
            "published": article.get("date", ""),
            "excerpt": article.get("metadata", {}).get("source_excerpt") or article.get("description", ""),
            "url": article.get("url", ""),
        }
        prompt = f"""Write a 180-250 word news analysis in the voice of {faculty.get('name', 'a faculty member')} for the Inquiry Institute.

Faculty areas: {', '.join(faculty.get('news_topics') or [])}
Faculty bio: {faculty.get('short_bio') or 'Not provided'}

Use only the source material below. Explain the core development, why it matters to this faculty member's areas, and one thoughtful question or limitation. Do not invent facts, quotations, sources, or personal experiences. Do not claim the faculty member read material beyond this excerpt. Do not use a headline, markdown, or citations in the prose; the site links the source separately.

Source material:
{json.dumps(source_material, ensure_ascii=False)}"""
        try:
            response = self.session.post(
                self.function_url,
                headers={
                    "Authorization": f"Bearer {config.SUPABASE_KEY}",
                    "apikey": config.SUPABASE_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "message": prompt,
                    "facultySlug": faculty.get("slug", ""),
                    "facultyName": faculty.get("name", "Faculty"),
                    "responseFormat": "json",
                    "generateTts": False,
                    "logToCommonplace": False,
                    "commonplaceMode": "off",
                },
                timeout=60,
            )
            if response.status_code != 200:
                raise RuntimeError(f"Edge Function returned HTTP {response.status_code}")
            summary = str(response.json().get("reply", "")).strip()
            return summary or self.fallback_summary(article)
        except Exception as error:
            print(f"⚠️  Gemini summary failed for {article.get('title', 'item')}: {error}")
            return self.fallback_summary(article)

    def enrich(self, articles: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Add a named author, detailed analysis, and source links to top items."""
        for article in articles:
            article["sources"] = self.source_record(article)

        for article in articles[:limit]:
            article.setdefault("metadata", {})
            faculty = self.select_author(article)
            if not faculty:
                article["faculty_summary"] = self.fallback_summary(article)
                continue
            article["faculty_author"] = {
                "name": faculty.get("name", "Faculty"),
                "slug": faculty.get("slug", ""),
            }
            article["faculty_summary"] = self.write_summary(article, faculty)
        return articles

"""Offline TF-IDF similarity and transparent routing rules; no paid API needed."""
from __future__ import annotations
import csv
import re
from pathlib import Path
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'data' / 'incidents.csv'

ROUTING = {
    'Network Support': ('vpn', 'wifi', 'wireless', 'network', 'dns', 'router', 'internet', 'connectivity'),
    'Identity & Access': ('password', 'login', 'sign in', 'account', 'mfa', 'authentication', 'locked'),
    'Workplace IT': ('laptop', 'printer', 'monitor', 'keyboard', 'desktop', 'battery'),
    'Application Support': ('application', 'app', 'portal', 'dashboard', 'page', 'error', 'crash'),
    'Database Operations': ('database', 'sql', 'query', 'postgres', 'mysql', 'deadlock'),
}

def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', text.lower())).strip()


def route_ticket(text: str) -> dict:
    """Explainable keyword-based assignment suggestion, not a trained classifier."""
    clean = ' ' + normalize(text) + ' '
    scores = {team: sum(1 for word in words if f' {word} ' in clean) for team, words in ROUTING.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return {'assignment_group': 'Service Desk', 'matched_keywords': [], 'method': 'fallback'}
    words = [word for word in ROUTING[best] if f' {word} ' in clean]
    return {'assignment_group': best, 'matched_keywords': words, 'method': 'keyword rules'}


def load_incidents(path: Path = DATA_PATH) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as f:
        entries = list(csv.DictReader(f))
    needed = {'number', 'short_description', 'description', 'assignment_group', 'state'}
    if not entries or not needed.issubset(entries[0]):
        raise ValueError('CSV must contain number, short_description, description, assignment_group and state')
    return entries


class IncidentMatcher:
    def __init__(self, incidents: list[dict]):
        if not incidents:
            raise ValueError('An incident collection is required')
        self.incidents = incidents
        self.documents = [normalize(f"{row['short_description']} {row['description']}") for row in incidents]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, title: str, description: str = '', top_k: int = 5, minimum_score: float = 0.1) -> list[dict]:
        if not title.strip():
            raise ValueError('Short description is required')
        if not 1 <= top_k <= 50:
            raise ValueError('top_k must be between 1 and 50')
        if not 0 <= minimum_score <= 1:
            raise ValueError('minimum_score must be between 0 and 1')
        query = normalize(f'{title} {description}')
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        ranking = sorted(range(len(scores)), key=lambda i: (-scores[i], self.incidents[i]['number']))
        return [{**self.incidents[i], 'similarity': round(float(scores[i]), 4)}
                for i in ranking if float(scores[i]) >= minimum_score][:top_k]


@lru_cache(maxsize=1)
def get_matcher() -> IncidentMatcher:
    return IncidentMatcher(load_incidents())


def analyze(title: str, description: str = '', top_k: int = 5, minimum_score: float = 0.1) -> dict:
    matches = get_matcher().search(title, description, top_k, minimum_score)
    routing = route_ticket(title + ' ' + description)
    return {'query': {'short_description': title, 'description': description},
            'suggested_assignment': routing, 'similar_incidents': matches,
            'possible_duplicate': bool(matches and matches[0]['similarity'] >= 0.65),
            'duplicate_threshold': 0.65,
            'disclaimer': 'Similarity suggestions require human review; no incident is created or modified.'}

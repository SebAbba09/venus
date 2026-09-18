from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "corpus"
RAW_DIR = CORPUS_DIR / "raw"
CLEAN_DIR = CORPUS_DIR / "clean"
MANIFEST_PATH = CORPUS_DIR / "manifest.json"
JSONL_PATH = CORPUS_DIR / "corpus.jsonl"

REQUEST_DELAY_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 30

USER_AGENT = (
    "Venus-M2-Research-Corpus/1.0 "
    "(academic RAG experiment; public ESTM pages)"
)


PAGES = [
    {
        "id": "ESTM_001",
        "title": "Formation initiale",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales",
    },
    {
        "id": "ESTM_002",
        "title": "Master Génie Logiciel et Administration Réseau",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/MGLAR/details",
    },
    {
        "id": "ESTM_003",
        "title": "Master Big Data et Intelligence artificielle",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/BDIA/details",
    },
    {
        "id": "ESTM_004",
        "title": "Master Sécurité des Systèmes d'Information",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/SSI/details",
    },
    {
        "id": "ESTM_005",
        "title": "Master Télécommunications et Réseaux",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/RT/details",
    },
    {
        "id": "ESTM_006",
        "title": "Formation à distance",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-a-distance",
    },
    {
        "id": "ESTM_007",
        "title": "Préinscription",
        "category": "admission",
        "url": "https://www.estm.sn/preinscription",
    },
    {
        "id": "ESTM_008",
        "title": "Nous contacter",
        "category": "institution",
        "url": "https://www.estm.sn/notre-ecole/contact",
    },
    {
        "id": "ESTM_009",
        "title": "Notre École",
        "category": "institution",
        "url": "https://www.estm.sn/notre-ecole",
    },
    {
        "id": "ESTM_010",
        "title": "Formation continue",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-continues",
    },
    {
        "id": "ESTM_011",
        "title": "Amicale des étudiants",
        "category": "vie_etudiante",
        "url": "https://www.estm.sn/vie-etudiante/amicale-etudiant",
    },
    {
        "id": "ESTM_012",
        "title": "Clubs",
        "category": "vie_etudiante",
        "url": "https://www.estm.sn/vie-etudiante/clubs",
    },
    {
        "id": "ESTM_013",
        "title": "Incubateur",
        "category": "vie_etudiante",
        "url": "https://www.estm.sn/vie-etudiante/incubateur",
    },
    {
        "id": "ESTM_014",
        "title": "Écoles et Universités partenaires",
        "category": "international",
        "url": "https://www.estm.sn/internationale/ecoles-et-universites-partenaires",
    },
    {
        "id": "ESTM_015",
        "title": "Programmes d'échanges à l'étranger",
        "category": "international",
        "url": "https://www.estm.sn/internationale/programmes-d-echange-a-etranger",
    },
    {
        "id": "ESTM_016",
        "title": "Stages et emplois",
        "category": "entreprises",
        "url": "https://www.estm.sn/entreprises/stages-emplois",
    },
    {
        "id": "ESTM_017",
        "title": "Entreprises partenaires",
        "category": "entreprises",
        "url": "https://www.estm.sn/entreprises/entreprises-partenaires",
    },
    {
        "id": "ESTM_018",
        "title": "Alumni",
        "category": "institution",
        "url": "https://www.estm.sn/notre-ecole/alumnis",
    },
    {
        "id": "ESTM_019",
        "title": "Licence Télécommunications – Réseaux & Cybersécurité",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/RTC/details",
    },
    {
        "id": "ESTM_020",
        "title": "Licence Génie logiciel et Réseaux",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/GLAR/details",
    },
    {
        "id": "ESTM_021",
        "title": "Licence Communication, Informatique et Multimédia",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/CIM/details",
    },
    {
        "id": "ESTM_022",
        "title": "Licence Génie Électrique et Énergies Renouvelables",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/GEER/details",
    },
    {
        "id": "ESTM_023",
        "title": "Master Monétique et Transactions Sécurisées",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/MTS/details",
    },
    {
        "id": "ESTM_024",
        "title": "Master Génie Électrique et Énergies Renouvelables",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/MGEER/details",
    },
    {
        "id": "ESTM_025",
        "title": "Master Ingénierie des Ressources Humaines",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/GRH/details",
    },
    {
        "id": "ESTM_026",
        "title": "Master Management de projets et Innovation",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/MPI/details",
    },
    {
        "id": "ESTM_027",
        "title": "Master Marketing-Communication",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/MC/details",
    },
    {
        "id": "ESTM_028",
        "title": "Licence Sciences de gestion",
        "category": "formations",
        "url": "https://www.estm.sn/nos-formations/formations-initiales/SG/details",
    },
]

class ESTMHTMLParser(HTMLParser):
    """
    Extraction HTML légère sans dépendance externe.

    Priorité :
    1. contenu de <main> s'il existe ;
    2. sinon contenu global en excluant les blocs inutiles.
    """

    SKIP_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "nav",
        "footer",
        "form",
        "button",
    }

    SKIP_CLASS_TOKENS = {
        "breadcrumb-estm",
        "btn",
        "cookie-consent",
        "dropdown-menu",
        "large-screen",
        "mask",
        "modal",
        "nav",
        "navbar",
        "small-screen",
        "text-estm",
        "view",
    }

    BLOCK_TAGS = {
        "p",
        "div",
        "section",
        "article",
        "main",
        "header",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "ul",
        "ol",
        "table",
        "tr",
        "td",
        "th",
        "br",
    }

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.skip_depth = 0
        self.main_depth: Optional[int] = None
        self.in_main = False
        self.title_parts: List[str] = []
        self.text_parts: List[str] = []
        self.before_main_parts: List[str] = []
        self.current_tag_stack: List[str] = []
        self.skipped_elements: List[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self.current_tag_stack.append(tag)

        attributes = dict(attrs)
        class_tokens = set((attributes.get("class") or "").split())
        element_id = attributes.get("id") or ""
        should_skip = (
            tag in self.SKIP_TAGS
            or bool(class_tokens & self.SKIP_CLASS_TOKENS)
            or "modal" in element_id.lower()
        )
        if should_skip:
            self.skip_depth += 1
            self.skipped_elements.append(tag)

        if tag == "main" and self.main_depth is None:
            self.main_depth = self.depth
            self.in_main = True

        if tag in self.BLOCK_TAGS and self.skip_depth == 0:
            self.text_parts.append("\n")

        self.depth += 1

    def handle_startendtag(self, tag, attrs):
        if tag.lower() in self.BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()

        self.depth = max(0, self.depth - 1)

        if tag == "main" and self.in_main:
            self.in_main = False

        if tag in self.SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1

        if self.current_tag_stack:
            # Remove the last matching tag where possible.
            for index in range(len(self.current_tag_stack) - 1, -1, -1):
                if self.current_tag_stack[index] == tag:
                    del self.current_tag_stack[index]
                    break

        if tag in self.skipped_elements:
            self.skipped_elements.remove(tag)
            self.skip_depth = max(0, self.skip_depth - 1)

        if tag in self.BLOCK_TAGS and self.skip_depth == 0:
            self.text_parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth > 0:
            return

        text = data.strip()
        if not text:
            return

        if self.current_tag_stack and self.current_tag_stack[-1] == "title":
            self.title_parts.append(text)

        # If <main> exists, prefer its content.
        if self.main_depth is not None and self.depth < self.main_depth:
            return

        if self.main_depth is None:
            self.before_main_parts.append(text)
        else:
            self.text_parts.append(text)

    def get_title(self) -> str:
        return normalize_text(" ".join(self.title_parts))

    def get_text(self) -> str:
        parts = self.text_parts if self.main_depth is not None else self.before_main_parts
        return normalize_text("\n".join(parts))


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = []
    previous_blank = False

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            if not previous_blank:
                lines.append("")
            previous_blank = True
            continue

        lines.append(line)
        previous_blank = False

    text = "\n".join(lines)
    return text.strip()


def decode_response(data: bytes, content_type: str) -> str:
    charset = "utf-8"

    match = re.search(r"charset=([a-zA-Z0-9._-]+)", content_type or "")
    if match:
        charset = match.group(1)

    try:
        return data.decode(charset, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch_page(url: str) -> Dict:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.5",
        },
    )

    started = time.perf_counter()

    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        raw_data = response.read()
        content_type = response.headers.get("Content-Type", "")
        final_url = response.geturl()

        elapsed = time.perf_counter() - started

        html = decode_response(raw_data, content_type)

        parser = ESTMHTMLParser()
        parser.feed(html)
        parser.close()

        extracted_title = parser.get_title()
        content = parser.get_text()

        return {
            "raw_html": html,
            "final_url": final_url,
            "content_type": content_type,
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "title_from_page": extracted_title,
            "content": content,
            "elapsed_seconds": round(elapsed, 4),
        }


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_jsonl(path: Path, rows: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(row, ensure_ascii=False)
                + "\n"
            )


def main():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    captured_at = datetime.now(timezone.utc).isoformat()

    records = []
    errors = []

    total = len(PAGES)

    print("=" * 72)
    print("VENUS M2 — ESTM PUBLIC CORPUS COLLECTOR")
    print("=" * 72)
    print(f"Documents à récupérer : {total}")
    print(f"Date de snapshot      : {captured_at}")
    print()

    for index, page in enumerate(PAGES, start=1):
        print(f"[{index:02d}/{total:02d}] {page['id']} — {page['title']}")

        try:
            result = fetch_page(page["url"])

            content = result["content"]

            if not content.strip():
                raise ValueError(
                    "Contenu extrait vide."
                )

            content_hash = sha256_text(content)

            raw_path = RAW_DIR / f"{page['id']}.html"
            clean_path = CLEAN_DIR / f"{page['id']}.txt"

            raw_path.write_text(
                result["raw_html"],
                encoding="utf-8",
            )

            header = (
                f"TITLE: {page['title']}\n"
                f"ID: {page['id']}\n"
                f"CATEGORY: {page['category']}\n"
                f"URL: {page['url']}\n"
                f"CAPTURED_AT: {captured_at}\n"
                f"SHA256: {content_hash}\n"
                f"\n"
            )

            clean_path.write_text(
                header + content,
                encoding="utf-8",
            )

            record = {
                "id": page["id"],
                "title": page["title"],
                "title_from_page": result["title_from_page"],
                "category": page["category"],
                "source_type": "public_web",
                "official_domain": True,
                "url": page["url"],
                "final_url": result["final_url"],
                "captured_at": captured_at,
                "sha256": content_hash,
                "content_type": result["content_type"],
                "etag": result["etag"],
                "last_modified": result["last_modified"],
                "character_count": len(content),
                "word_count": len(content.split()),
                "raw_file": str(raw_path.relative_to(CORPUS_DIR)),
                "clean_file": str(clean_path.relative_to(CORPUS_DIR)),
                "content": content,
            }

            records.append(record)

            print(
                f"      OK — {len(content):,} caractères "
                f"/ {len(content.split()):,} mots"
            )

        except HTTPError as exc:
            error = {
                "id": page["id"],
                "title": page["title"],
                "url": page["url"],
                "error": f"HTTP {exc.code}: {exc.reason}",
            }
            errors.append(error)
            print(f"      ERREUR — HTTP {exc.code}: {exc.reason}")

        except URLError as exc:
            error = {
                "id": page["id"],
                "title": page["title"],
                "url": page["url"],
                "error": f"URL error: {exc.reason}",
            }
            errors.append(error)
            print(f"      ERREUR — réseau : {exc.reason}")

        except Exception as exc:
            error = {
                "id": page["id"],
                "title": page["title"],
                "url": page["url"],
                "error": repr(exc),
            }
            errors.append(error)
            print(f"      ERREUR — {exc}")

        if index < total:
            time.sleep(REQUEST_DELAY_SECONDS)

    manifest = {
        "dataset_name": "ESTM-public-snapshot",
        "dataset_version": "2026-09-18",
        "captured_at": captured_at,
        "source_domain": "www.estm.sn",
        "source_description": (
            "Pages publiques de l'ESTM utilisées pour les expériences "
            "d'embeddings de Venus M2."
        ),
        "documents_requested": total,
        "documents_successful": len(records),
        "documents_failed": len(errors),
        "records": [
            {
                key: value
                for key, value in record.items()
                if key != "content"
            }
            for record in records
        ],
        "errors": errors,
    }

    save_json(MANIFEST_PATH, manifest)
    save_jsonl(JSONL_PATH, records)

    print()
    print("=" * 72)
    print("RÉSULTAT")
    print("=" * 72)
    print(f"Documents réussis : {len(records)}")
    print(f"Documents échoués : {len(errors)}")
    print(f"Manifest          : {MANIFEST_PATH}")
    print(f"Corpus JSONL      : {JSONL_PATH}")
    print(f"Corpus nettoyé    : {CLEAN_DIR}")
    print(f"HTML originaux    : {RAW_DIR}")

    if errors:
        print()
        print("Documents en erreur :")
        for error in errors:
            print(
                f"- {error['id']} — {error['title']} : "
                f"{error['error']}"
            )

    print()
    print("Snapshot terminé.")


if __name__ == "__main__":
    main()

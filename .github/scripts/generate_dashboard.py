from __future__ import annotations

import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

USERNAME = "M4rc3low"
API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "")


def api_get(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "M4rc3low-profile-dashboard",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def shorten(text: str | None, limit: int) -> str:
    if not text:
        return "Projeto em evolução"
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def main():
    try:
        user = api_get(f"{API}/users/{USERNAME}")
        repos = api_get(f"{API}/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated")
    except Exception as exc:
        print(f"GitHub API unavailable: {exc}")
        user = {"public_repos": 0, "followers": 0}
        repos = []

    repos = [repo for repo in repos if not repo.get("fork")]
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    forks = sum(repo.get("forks_count", 0) for repo in repos)

    languages = Counter()
    for repo in repos:
        try:
            for language, amount in api_get(repo["languages_url"]).items():
                languages[language] += amount
        except Exception:
            language = repo.get("language")
            if language:
                languages[language] += 1

    top_languages = languages.most_common(6)
    total_language = sum(value for _, value in top_languages) or 1

    featured_order = [
        "peritolex-app",
        "geoterritorios-marcelo-app",
        "amm-materiais-construcao",
        "aws-monitoring-lab",
        "terraform-aws-lab",
    ]
    repo_map = {repo["name"]: repo for repo in repos}
    featured = [repo_map[name] for name in featured_order if name in repo_map][:5]
    if not featured:
        featured = repos[:5]

    colors = {
        "JavaScript": "#f7df1e",
        "TypeScript": "#3178c6",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Python": "#3572A5",
        "Java": "#b07219",
        "HCL": "#844fba",
        "Shell": "#89e051",
        "PHP": "#4F5D95",
    }

    out = []
    add = out.append
    add('<svg width="1000" height="760" viewBox="0 0 1000 760" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub dashboard de Marcelo Gomes">')
    add('<rect width="1000" height="760" rx="22" fill="#0d1117"/>')
    add('<rect x="1" y="1" width="998" height="758" rx="21" fill="none" stroke="#30363d"/>')
    add('<rect x="0" y="0" width="1000" height="8" rx="4" fill="#7c3aed"/>')

    # Header
    add('<text x="48" y="68" fill="#f0f6fc" font-family="Segoe UI,Arial,sans-serif" font-size="31" font-weight="700">Marcelo Gomes</text>')
    add('<text x="48" y="99" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="17">Software Development  •  Cloud  •  DevOps</text>')
    add('<circle cx="48" cy="130" r="5" fill="#3fb950"/>')
    add('<text x="62" y="136" fill="#c9d1d9" font-family="Segoe UI,Arial,sans-serif" font-size="14">Construindo, automatizando e evoluindo projetos reais</text>')

    # Metric cards
    metrics = [
        ("Repositórios públicos", str(user.get("public_repos", len(repos))), "#58a6ff"),
        ("Stars recebidas", str(stars), "#e3b341"),
        ("Forks", str(forks), "#a371f7"),
        ("Seguidores", str(user.get("followers", 0)), "#3fb950"),
    ]
    card_w = 212
    for i, (label, value, color) in enumerate(metrics):
        x = 48 + i * 232
        add(f'<rect x="{x}" y="168" width="{card_w}" height="94" rx="12" fill="#161b22" stroke="#30363d"/>')
        add(f'<circle cx="{x+24}" cy="195" r="6" fill="{color}"/>')
        add(f'<text x="{x+38}" y="201" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="13">{escape(label)}</text>')
        add(f'<text x="{x+20}" y="239" fill="#f0f6fc" font-family="Segoe UI,Arial,sans-serif" font-size="27" font-weight="700">{escape(value)}</text>')

    # Languages
    add('<text x="48" y="312" fill="#f0f6fc" font-family="Segoe UI,Arial,sans-serif" font-size="21" font-weight="700">Linguagens nos projetos públicos</text>')
    y = 346
    if top_languages:
        for language, amount in top_languages:
            percent = amount / total_language
            width = max(8, int(340 * percent))
            color = colors.get(language, "#58a6ff")
            add(f'<text x="48" y="{y+13}" fill="#c9d1d9" font-family="Segoe UI,Arial,sans-serif" font-size="13">{escape(language)}</text>')
            add(f'<rect x="148" y="{y}" width="340" height="14" rx="7" fill="#21262d"/>')
            add(f'<rect x="148" y="{y}" width="{width}" height="14" rx="7" fill="{color}"/>')
            add(f'<text x="498" y="{y+13}" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="12">{percent*100:.1f}%</text>')
            y += 31
    else:
        add('<text x="48" y="365" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="14">Os dados serão preenchidos na próxima atualização.</text>')

    # Focus card
    add('<rect x="570" y="296" width="382" height="205" rx="14" fill="#161b22" stroke="#30363d"/>')
    add('<text x="594" y="330" fill="#f0f6fc" font-family="Segoe UI,Arial,sans-serif" font-size="20" font-weight="700">Foco técnico</text>')
    focus = [
        ("AWS", "Cloud"),
        ("Docker", "Containers"),
        ("Terraform", "Infrastructure as Code"),
        ("Kubernetes", "Orquestração"),
        ("GitHub Actions", "CI/CD"),
        ("Grafana + Zabbix", "Observabilidade"),
    ]
    fy = 365
    for name, desc in focus:
        add(f'<circle cx="596" cy="{fy-5}" r="4" fill="#7c3aed"/>')
        add(f'<text x="610" y="{fy}" fill="#c9d1d9" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="600">{escape(name)}</text>')
        add(f'<text x="748" y="{fy}" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="13">{escape(desc)}</text>')
        fy += 24

    # Featured repositories
    add('<text x="48" y="548" fill="#f0f6fc" font-family="Segoe UI,Arial,sans-serif" font-size="21" font-weight="700">Projetos em destaque</text>')
    ry = 583
    for idx, repo in enumerate(featured):
        col = idx % 2
        row = idx // 2
        x = 48 + col * 466
        y0 = ry + row * 58
        name = shorten(repo.get("name"), 34)
        desc = shorten(repo.get("description"), 48)
        lang = repo.get("language") or "Projeto"
        stars_n = repo.get("stargazers_count", 0)
        add(f'<rect x="{x}" y="{y0-22}" width="438" height="50" rx="9" fill="#161b22" stroke="#30363d"/>')
        add(f'<text x="{x+14}" y="{y0}" fill="#58a6ff" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700">{escape(name)}</text>')
        add(f'<text x="{x+14}" y="{y0+19}" fill="#8b949e" font-family="Segoe UI,Arial,sans-serif" font-size="11">{escape(desc)}</text>')
        add(f'<text x="{x+350}" y="{y0}" fill="#c9d1d9" font-family="Segoe UI,Arial,sans-serif" font-size="11">{escape(lang)}  ★ {stars_n}</text>')

    updated = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    add(f'<text x="48" y="735" fill="#6e7681" font-family="Segoe UI,Arial,sans-serif" font-size="11">Atualizado automaticamente em {updated}</text>')
    add('<text x="952" y="735" text-anchor="end" fill="#6e7681" font-family="Segoe UI,Arial,sans-serif" font-size="11">github.com/M4rc3low</text>')
    add('</svg>')

    output = Path("assets/github-dashboard.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(out), encoding="utf-8")
    print(f"Generated {output}")


if __name__ == "__main__":
    main()

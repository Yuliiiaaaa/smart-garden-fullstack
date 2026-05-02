# app/api/endpoints/seo.py
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import get_db, Garden

router = APIRouter()


@router.get("/robots.txt", include_in_schema=False)
async def robots():
    """robots.txt для поисковых систем"""
    content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /dashboard
Disallow: /analysis
Disallow: /admin
Disallow: /auth

Sitemap: https://smart-garden.ru/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap(db: Session = Depends(get_db)):
    """Динамическая карта сайта для поисковых систем"""
    base_url = "https://smart-garden.ru"
    now = datetime.utcnow().isoformat()
    urls = []

    # Статические страницы (публичные, индексируемые)
    static_pages = [
        ("/", 1.0, "Главная страница Smart Garden"),
        ("/auth", 0.5, "Страница входа и регистрации"),
        ("/about", 0.7, "О проекте Smart Garden"),
    ]

    for page, priority, _ in static_pages:
        urls.append(f"""
        <url>
            <loc>{base_url}{page}</loc>
            <lastmod>{now}</lastmod>
            <priority>{priority}</priority>
        </url>
        """)

    # Динамические страницы садов (публичные, если доступны)
    gardens = db.query(Garden).all()
    for garden in gardens:
        lastmod = garden.updated_at.isoformat() if garden.updated_at else now
        urls.append(f"""
        <url>
            <loc>{base_url}/gardens/{garden.id}</loc>
            <lastmod>{lastmod}</lastmod>
            <priority>0.6</priority>
            <image:image>
                <image:loc>{base_url}/static/garden-placeholder.jpg</image:loc>
                <image:title>{garden.name}</image:title>
            </image:image>
        </url>
        """)

    # Закрытые страницы (не индексируются)
    private_pages = [
        "/dashboard",
        "/analysis",
        "/analytics",
        "/history",
        "/gardens/manage",
        "/admin/users",
    ]

    for page in private_pages:
        urls.append(f"""
        <url>
            <loc>{base_url}{page}</loc>
            <lastmod>{now}</lastmod>
            <priority>0.0</priority>
        </url>
        """)

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{''.join(urls)}
</urlset>"""

    return Response(content=sitemap_xml.strip(), media_type="application/xml")

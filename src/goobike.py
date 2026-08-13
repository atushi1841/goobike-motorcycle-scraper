import asyncio
import re
import httpx
from bs4 import BeautifulSoup

KNOWN_MAKERS = [
    "ホンダ",
    "ヤマハ",
    "スズキ",
    "カワサキ",
    "ＢＭＷ",
    "BMW",
    "ハーレーダビッドソン",
    "ドゥカティ",
    "KTM",
    "ＫＴＭ",
]

async def fetch_page(client: httpx.AsyncClient, url: str):
    for attempt in range(3):
        try:
            resp = await client.get(url, follow_redirects=True)
            if resp.status_code == 200:
                resp.encoding = "utf-8"
                return resp.text
            if resp.status_code == 429 or resp.status_code >= 500:
                await asyncio.sleep(2 ** attempt)
                continue
            return None
        except (httpx.HTTPError, OSError):
            await asyncio.sleep(2 ** attempt)
            continue
    return None

def _clean_price_text(s):
    s = s.replace(" ", "").replace("\u3000", "")
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*万円', s)
    if not m:
        m = re.search(r'([\d,]+(?:\.\d+)?)', s)
    if not m:
        return None
    try:
        val = float(m.group(1).replace(',', ''))
        return int(val * 10000)
    except (TypeError, ValueError):
        return None

def _extract_field(text, pattern, default=None):
    m = re.search(pattern, text)
    if m:
        return m.group(1).strip()
    return default

def parse_page(html: str):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    cards = soup.select("div[stock_id]")
    if not cards:
        cards = soup.select("div.textBox")
    for card in cards:
        detail_link = card.select_one('a[href*="/spread/"]')
        if not detail_link:
            continue
        href = detail_link.get("href", "")
        id_match = re.search(r"/spread/([^/]+)/index\.html", href)
        item_id = id_match.group(1) if id_match else None

        brand_elem = card.select_one("span.BrandName")
        maker = brand_elem.get_text(strip=True) if brand_elem else None
        carname_elem = card.select_one("span.CarName")
        title = carname_elem.get_text(strip=True) if carname_elem else None
        if not title and detail_link:
            title = detail_link.get_text(strip=True)

        if not maker:
            if title:
                maker = title.split()[0]

        price_elem = card.select_one("span.totalPrice")
        price = None
        if price_elem:
            price = _clean_price_text(price_elem.get_text(" ", strip=True))
        if price is None:
            card_text_full = card.get_text(" ", strip=True)
            m = re.search(r'支払総額\s*[:：]?\s*([\d,]+(?:\.\d+)?)\s*万円', card_text_full)
            if m:
                try:
                    price = int(float(m.group(1).replace(',', '')) * 10000)
                except (ValueError, TypeError):
                    price = None

        img_tag = card.find("img")
        image_url = None
        if img_tag:
            src = img_tag.get("src") or ""
            if "picture.goobike.com" in src:
                image_url = src
            else:
                image_url = img_tag.get("data-src") or None

        detail_url = None
        if href:
            if href.startswith("http"):
                detail_url = href
            else:
                detail_url = "https://www.goobike.com" + href

        year = None
        displacement = None
        mileage = None
        repair_history = None
        location = None
        shop = None
        phone = None

        # 各pタグからテキストを取得して年式・排気量・走行距離・修復歴を抽出
        for p in card.select("p"):
            p_text = p.get_text(" ", strip=True)

            if year is None:
                if "モデル年式" in p_text:
                    year = _extract_field(p_text, r'モデル年式\s*[:：]?\s*(.+)')
                elif "初度登録年" in p_text:
                    year = _extract_field(p_text, r'初度登録年\s*[:：]?\s*(.+)')

            if displacement is None:
                m = re.search(r'排気量\s*[:：]?\s*([0-9]+)\s*cc', p_text, re.IGNORECASE)
                if m:
                    displacement = m.group(1) + "cc"

            if mileage is None:
                # 例: 走行距離 ： 2316 Km
                m = re.search(r'走行距離\s*[:：]?\s*([0-9,]+(?:\.\d+)?)\s*(?:km|キロ)?', p_text, re.IGNORECASE)
                if m:
                    mileage = m.group(1).replace(',', '') + " km"

            if repair_history is None:
                if "修復歴" in p_text:
                    repair_history = _extract_field(p_text, r'修復歴\s*[:：]?\s*(.+)')

        # 所在地・店舗名（store_name）
        store_elem = card.select_one("p.store_name")
        if store_elem:
            span = store_elem.find("span")
            if span:
                shop = span.get_text(strip=True)
                # 所在地はspan以外のテキスト
                location = ""
                for child in store_elem.children:
                    if getattr(child, "name", None) == "span":
                        continue
                    if child.string:
                        location += child.string
                location = location.strip()
            else:
                location = store_elem.get_text(" ", strip=True)

        # 電話番号
        tel_elem = card.select_one("div.store_tel")
        if tel_elem:
            m = re.search(r'(\d{1,5}-\d{1,4}-\d{3,4})', tel_elem.get_text(" ", strip=True))
            if m:
                phone = m.group(1)

        results.append({
            "itemId": item_id,
            "title": title,
            "maker": maker,
            "price": price,
            "imageUrl": image_url,
            "detailUrl": detail_url,
            "year": year,
            "displacement": displacement,
            "mileage": mileage,
            "repairHistory": repair_history,
            "location": location,
            "shop": shop,
            "phone": phone,
            "source": "goobike",
        })
    return results

def list_page(base: str, page: int) -> str:
    if page <= 1:
        return base
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}page={page}"

#!/usr/bin/env python3
"""
Program pro webscraping stránek obsahujících hledané jméno
Autor: Petr Rýdlo
Verze 2.0 - Vyhledává stránky s jménem na webu a analyzuje je
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import re
from collections import Counter
import time


def nacti_stranku(url, timeout=10):
    """Načte HTML obsah stránky"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ Chyba při načítání {url}: {e}")
        return None


def analyzuj_odkazy(soup, base_url):
    """Analyzuje všechny odkazy na stránce"""
    odkazy = soup.find_all('a', href=True)

    typy_odkazu = {
        'interni': [],
        'externi': [],
        'kotvy': []
    }

    for odkaz in odkazy:
        href = odkaz['href']
        text = odkaz.get_text(strip=True)

        if href.startswith('#'):
            typy_odkazu['kotvy'].append({'href': href, 'text': text})
        elif href.startswith('http'):
            if urlparse(base_url).netloc in href:
                typy_odkazu['interni'].append({'href': href, 'text': text})
            else:
                typy_odkazu['externi'].append({'href': href, 'text': text})
        elif href.startswith('/'):
            typy_odkazu['interni'].append({'href': urljoin(base_url, href), 'text': text})

    return typy_odkazu


def analyzuj_nadpisy(soup):
    """Analyzuje všechny nadpisy na stránce"""
    nadpisy = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        if h_tags:
            nadpisy[f'h{i}'] = [h.get_text(strip=True) for h in h_tags]
    return nadpisy


def analyzuj_odstavce(soup):
    """Analyzuje všechny odstavce na stránce"""
    odstavce = soup.find_all('p')
    return [p.get_text(strip=True) for p in odstavce if p.get_text(strip=True)]


def najdi_jmeno_v_textu(soup, hledane_jmeno):
    """Najde všechny výskyty hledaného jména na stránce"""
    nalezene_vyskyty = []

    # Hledání v různých typech tagů
    for tag_name in ['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                      'span', 'td', 'th', 'a', 'strong', 'b', 'em', 'i']:
        tagy = soup.find_all(tag_name)
        for tag in tagy:
            text = tag.get_text()
            if hledane_jmeno.lower() in text.lower():
                # Najdi kontext kolem jména
                pozice = text.lower().find(hledane_jmeno.lower())
                kontext_start = max(0, pozice - 50)
                kontext_end = min(len(text), pozice + len(hledane_jmeno) + 50)
                kontext = text[kontext_start:kontext_end].strip()

                # Najdi nadřazený element
                parent = tag.parent
                parent_info = {
                    'tag': parent.name if parent else None,
                    'class': ' '.join(parent.get('class', [])) if parent and parent.get('class') else None,
                    'id': parent.get('id') if parent else None
                }

                nalezene_vyskyty.append({
                    'tag': tag_name,
                    'text': text.strip()[:200],  # Prvních 200 znaků
                    'kontext': kontext,
                    'parent': parent_info,
                    'element': tag
                })

    return nalezene_vyskyty


def analyzuj_stranku(url, hledane_jmeno):
    """Provede kompletní analýzu jedné stránky"""
    print(f"\n📄 Analyzuji: {url}")
    print("="*60)

    # Načtení stránky
    html_content = nacti_stranku(url)
    if not html_content:
        return None

    # Parsování HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Získání názvu stránky
    title = soup.find('title')
    title_text = title.get_text() if title else "Bez názvu"
    print(f"   📖 Název: {title_text}")

    # Analýzy
    odkazy = analyzuj_odkazy(soup, url)
    nadpisy = analyzuj_nadpisy(soup)
    odstavce = analyzuj_odstavce(soup)
    nalezene = najdi_jmeno_v_textu(soup, hledane_jmeno)

    # Výsledky
    print(f"\n   📊 STATISTIKY:")
    print(f"      • Odkazy: {len(odkazy['interni'])} interních, {len(odkazy['externi'])} externích")
    print(f"      • Nadpisy: {sum(len(v) for v in nadpisy.values())} celkem")
    print(f"      • Odstavce: {len(odstavce)}")

    if nalezene:
        print(f"\n   🎯 NALEZENO JMÉNO '{hledane_jmeno}':")
        print(f"      • Počet výskytů: {len(nalezene)}")

        # Zobraz první výskyt
        prvni = nalezene[0]
        print(f"\n   📌 První výskyt:")
        print(f"      • Tag: <{prvni['tag']}>")
        print(f"      • Kontext: ...{prvni['kontext']}...")

        if prvni['parent']['tag']:
            print(f"      • Nadřazený tag: <{prvni['parent']['tag']}>", end="")
            if prvni['parent']['class']:
                print(f" class='{prvni['parent']['class']}'", end="")
            if prvni['parent']['id']:
                print(f" id='{prvni['parent']['id']}'", end="")
            print()

        # Statistika tagů
        tag_counts = Counter(item['tag'] for item in nalezene)
        print(f"\n   📊 Výskyty podle tagů:")
        for tag, count in tag_counts.most_common(5):
            print(f"      • <{tag}>: {count}x")
    else:
        print(f"\n   ❌ Jméno '{hledane_jmeno}' nebylo nalezeno")

    return {
        'url': url,
        'title': title_text,
        'nadpisy': nadpisy,
        'pocet_odkazu': {
            'interni': len(odkazy['interni']),
            'externi': len(odkazy['externi'])
        },
        'pocet_odstavcu': len(odstavce),
        'nalezene_vyskyty': len(nalezene) if nalezene else 0,
        'vyskyty_detail': [
            {
                'tag': v['tag'],
                'kontext': v['kontext'],
                'parent_tag': v['parent']['tag']
            } for v in nalezene[:5]  # Max 5 ukázek
        ] if nalezene else []
    }


def main():
    """Hlavní funkce programu"""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║      WEBSCRAPER 2.0 - Vyhledávání na webu               ║")
    print("║                  Petr Rýdlo                              ║")
    print("╚══════════════════════════════════════════════════════════╝")

    hledane_jmeno = "Petr Rýdlo"

    # Seznam URL k analýze (nalezené stránky s vaším jménem)
    urls = [
        "https://www.antikavion.cz/autor/petr-rydlo",  # Stránka, kterou jste našel
        "https://gask.art/book/zaslouzily-umelec-petr-rydlo-obrazy-sklo/",  # GASK galerie
        "https://rejstrik-firem.kurzy.cz/osoby/372090/",  # Rejstřík firem
    ]

    print(f"\n🔍 Hledané jméno: '{hledane_jmeno}'")
    print(f"📋 Počet stránek k analýze: {len(urls)}")

    # Analýza každé stránky
    vysledky_vse = []
    uspesne_nalezeno = 0

    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"🌐 [{i}/{len(urls)}] STRÁNKA")

        vysledek = analyzuj_stranku(url, hledane_jmeno)

        if vysledek:
            vysledky_vse.append(vysledek)
            if vysledek['nalezene_vyskyty'] > 0:
                uspesne_nalezeno += 1

        # Krátká pauza mezi požadavky
        if i < len(urls):
            time.sleep(1)

    # Souhrn
    print("\n" + "="*60)
    print("📊 CELKOVÝ SOUHRN:")
    print(f"   • Analyzováno stránek: {len(vysledky_vse)}")
    print(f"   • Jméno nalezeno na: {uspesne_nalezeno} stránkách")

    if uspesne_nalezeno > 0:
        print(f"\n   ✅ Úspěšné nálezy:")
        for v in vysledky_vse:
            if v['nalezene_vyskyty'] > 0:
                print(f"      • {v['title'][:50]}...")
                print(f"        Výskytů: {v['nalezene_vyskyty']}")

    # Uložení výsledků
    output_file = "webscraping_vysledky_v2.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(vysledky_vse, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Výsledky uloženy do '{output_file}'")
    except Exception as e:
        print(f"❌ Chyba při ukládání: {e}")

    print("\n" + "="*60)
    print("Program ukončen.")

    return vysledky_vse


if __name__ == "__main__":
    main()
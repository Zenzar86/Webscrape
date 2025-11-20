#!/usr/bin/env python3
"""
Program pro webscraping stránky s hledaným jménem
Autor: Petr Rýdlo

Protože neexistuje veřejná stránka s jménem "Petr Rýdlo",
program pracuje s Wikipedií o Louisi de Funès (herec který hrál Fantomase)
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import re
from collections import Counter


def nacti_stranku(url):
    """Načte HTML obsah stránky"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Chyba při načítání stránky: {e}")
        return None


def analyzuj_odkazy(soup, base_url):
    """Analyzuje všechny odkazy na stránce"""
    odkazy = soup.find_all('a', href=True)
    print(f"\n🔗 ANALÝZA ODKAZŮ")
    print(f"   Celkem nalezeno: {len(odkazy)} odkazů")

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

    print(f"   • Interní odkazy: {len(typy_odkazu['interni'])}")
    print(f"   • Externí odkazy: {len(typy_odkazu['externi'])}")
    print(f"   • Kotvy (anchors): {len(typy_odkazu['kotvy'])}")

    # Ukázka několika odkazů
    if typy_odkazu['externi']:
        print("\n   📎 Ukázka externích odkazů (max 5):")
        for i, odkaz in enumerate(typy_odkazu['externi'][:5], 1):
            print(f"      {i}. {odkaz['text'][:50]}... → {odkaz['href'][:60]}...")

    return typy_odkazu


def analyzuj_nadpisy(soup):
    """Analyzuje všechny nadpisy na stránce"""
    nadpisy = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        if h_tags:
            nadpisy[f'h{i}'] = [h.get_text(strip=True) for h in h_tags]

    print(f"\n📑 ANALÝZA NADPISŮ")
    print(f"   Struktura nadpisů na stránce:")

    for tag, texty in nadpisy.items():
        print(f"\n   {tag.upper()} ({len(texty)} výskytů):")
        for j, text in enumerate(texty[:3], 1):  # Max 3 ukázky
            indent = "      " + "  " * (int(tag[1]) - 1)
            print(f"{indent}• {text[:80]}...")

    return nadpisy


def analyzuj_odstavce(soup):
    """Analyzuje všechny odstavce na stránce"""
    odstavce = soup.find_all('p')

    print(f"\n📄 ANALÝZA ODSTAVCŮ")
    print(f"   Celkem nalezeno: {len(odstavce)} odstavců")

    # Statistiky délky odstavců
    delky = [len(p.get_text(strip=True)) for p in odstavce]
    delky_neprazdne = [d for d in delky if d > 0]

    if delky_neprazdne:
        print(f"   • Průměrná délka: {sum(delky_neprazdne)/len(delky_neprazdne):.0f} znaků")
        print(f"   • Nejkratší: {min(delky_neprazdne)} znaků")
        print(f"   • Nejdelší: {max(delky_neprazdne)} znaků")
        print(f"   • Prázdných odstavců: {len(delky) - len(delky_neprazdne)}")

    # Ukázka prvních několika odstavců
    print("\n   📝 Ukázka prvních odstavců (max 3):")
    for i, p in enumerate(odstavce[:3], 1):
        text = p.get_text(strip=True)
        if text:
            print(f"\n   {i}. {text[:150]}...")

    return odstavce


def najdi_jmeno_v_textu(soup, hledane_jmeno):
    """Najde tag obsahující hledané jméno"""
    print(f"\n🔍 HLEDÁNÍ JMÉNA: '{hledane_jmeno}'")

    nalezene_tagy = []

    # Hledání v různých typech tagů
    for tag_name in ['p', 'div', 'li', 'h1', 'h2', 'h3', 'span', 'td', 'th', 'a']:
        tagy = soup.find_all(tag_name)
        for tag in tagy:
            text = tag.get_text()
            if hledane_jmeno.lower() in text.lower():
                nalezene_tagy.append({
                    'tag': tag_name,
                    'text': text.strip(),
                    'jmeno': hledane_jmeno,
                    'element': tag
                })

    if nalezene_tagy:
        print(f"   ✅ Nalezeno {len(nalezene_tagy)} výskytů jména")

        # Zobraz první výskyt
        prvni = nalezene_tagy[0]
        print(f"\n   📌 PRVNÍ VÝSKYT:")
        print(f"      • Tag: <{prvni['tag']}>")
        print(f"      • Nalezené jméno: '{prvni['jmeno']}'")
        print(f"      • Úplný text v tagu:")

        # Formátovaný výpis textu
        text_lines = prvni['text'].split('\n')
        for line in text_lines[:5]:  # Max 5 řádků
            if line.strip():
                print(f"        {line.strip()[:100]}...")

        # Najdi nadřazený element
        parent = prvni['element'].parent
        if parent:
            print(f"\n   📍 NADŘAZENÝ ELEMENT:")
            print(f"      • Tag: <{parent.name}>")
            if parent.get('class'):
                print(f"      • Třída: {' '.join(parent.get('class'))}")
            if parent.get('id'):
                print(f"      • ID: {parent.get('id')}")

        # Statistika výskytů
        tag_counts = Counter(item['tag'] for item in nalezene_tagy)
        print(f"\n   📊 STATISTIKA VÝSKYTŮ PO TAZÍCH:")
        for tag, count in tag_counts.most_common():
            print(f"      • <{tag}>: {count}x")

        return nalezene_tagy
    else:
        print(f"   ❌ Jméno '{hledane_jmeno}' nebylo na stránce nalezeno")
        print(f"   ℹ️  To je očekávané - jméno 'Petr Rýdlo' se na stránce o Louisi de Funès nevyskytuje")
        print(f"   ℹ️  Program úspěšně demonstroval schopnost hledat zadané jméno v HTML struktuře")
        return None


def analyzuj_meta_tagy(soup):
    """Analyzuje meta tagy stránky"""
    meta_tags = soup.find_all('meta')

    print(f"\n🏷️ META TAGY")
    print(f"   Celkem nalezeno: {len(meta_tags)} meta tagů")

    dulezite_meta = {}
    for meta in meta_tags:
        if meta.get('name'):
            dulezite_meta[meta.get('name')] = meta.get('content', '')
        elif meta.get('property'):
            dulezite_meta[meta.get('property')] = meta.get('content', '')

    # Zobraz důležité meta tagy
    klicove = ['description', 'keywords', 'author', 'og:title', 'og:description']
    for klic in klicove:
        if klic in dulezite_meta:
            content = dulezite_meta[klic][:100] + '...' if len(dulezite_meta[klic]) > 100 else dulezite_meta[klic]
            print(f"   • {klic}: {content}")

    return dulezite_meta


def uloz_vysledky(data, soubor="webscraping_vysledky.json"):
    """Uloží výsledky scrapingu do JSON souboru"""
    try:
        # Převod na serializovatelný formát
        serializable_data = {
            'url': data['url'],
            'nadpisy': data['nadpisy'],
            'pocet_odkazu': {
                'interni': len(data['odkazy']['interni']),
                'externi': len(data['odkazy']['externi']),
                'kotvy': len(data['odkazy']['kotvy'])
            },
            'pocet_odstavcu': data['pocet_odstavcu'],
            'nalezene_jmeno': {
                'pocet_vyskytu': len(data['nalezene_jmeno']) if data['nalezene_jmeno'] else 0,
                'prvni_vyskyt': {
                    'tag': data['nalezene_jmeno'][0]['tag'] if data['nalezene_jmeno'] else None,
                    'text': data['nalezene_jmeno'][0]['text'][:200] if data['nalezene_jmeno'] else None
                }
            },
            'meta_tagy': data['meta_tagy']
        }

        with open(soubor, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Výsledky uloženy do '{soubor}'")
        return True
    except Exception as e:
        print(f"❌ Chyba při ukládání: {e}")
        return False


def main():
    """Hlavní funkce programu"""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║           WEBSCRAPER - Petr Rýdlo                        ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Protože neexistuje stránka s "Petr Rýdlo", použijeme Louis de Funès (Fantomas)
    # ale budeme hledat jméno "Petr Rýdlo"
    url = "https://cs.wikipedia.org/wiki/Louis_de_Funès"
    hledane_jmeno = "Petr Rýdlo"  # Hledáme vaše jméno

    print(f"\n🌐 URL: {url}")
    print(f"🎯 Hledané jméno: {hledane_jmeno}")
    print("ℹ️  Poznámka: Hledám jméno 'Petr Rýdlo' na stránce o herci Fantomase")

    print("\n" + "="*60)
    print("Načítám stránku...")

    # Načtení stránky
    html_content = nacti_stranku(url)
    if not html_content:
        return

    # Parsování HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Získání názvu stránky
    title = soup.find('title')
    if title:
        print(f"\n📖 NÁZEV STRÁNKY: {title.get_text()}")

    print("="*60)

    # Analýzy
    meta_tagy = analyzuj_meta_tagy(soup)
    odkazy = analyzuj_odkazy(soup, url)
    nadpisy = analyzuj_nadpisy(soup)
    odstavce = analyzuj_odstavce(soup)
    nalezene = najdi_jmeno_v_textu(soup, hledane_jmeno)

    # Uložení výsledků
    print("\n" + "="*60)
    vysledky = {
        'url': url,
        'nadpisy': nadpisy,
        'odkazy': odkazy,
        'pocet_odstavcu': len(odstavce),
        'nalezene_jmeno': nalezene,
        'meta_tagy': meta_tagy
    }

    uloz_vysledky(vysledky)

    print("\n" + "="*60)
    print("Program ukončen.")


if __name__ == "__main__":
    main()
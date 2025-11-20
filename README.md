# Webscraper

Program pro webscraping veřejné stránky s hledaným jménem.

## Autor
Petr Rýdlo

## Popis
Program provádí webscraping stránky a analyzuje:
- Všechny odkazy (interní, externí, kotvy)
- Nadpisy všech úrovní (h1-h6)
- Odstavce a jejich statistiky
- Meta tagy
- **Vyhledává jméno "Petr Rýdlo" v textu a určuje nadřazený tag**

Vzhledem k tomu, že neexistuje veřejná stránka s jménem "Petr Rýdlo", program používá alternativní možnost ze zadání - Wikipedia stránku o Louisi de Funès (herec, který hrál Fantomase), ale hledá jméno "Petr Rýdlo".

## Požadavky
```bash
pip install requests beautifulsoup4
```

## Použití
```bash
python3 webscraper.py
```

Program automaticky načte Wikipedii o Louisi de Funès a provede kompletní analýzu.

## Výstup
Program zobrazí výsledky v konzoli a uloží strukturovaná data do JSON souboru `webscraping_vysledky.json`.

## Příklad výstupu
```
🔗 ANALÝZA ODKAZŮ
   Celkem nalezeno: 588 odkazů
   • Interní odkazy: 417
   • Externí odkazy: 136
   • Kotvy (anchors): 35

📑 ANALÝZA NADPISŮ
   H1 (1 výskytů): Louis de Funès
   H2 (5 výskytů): Obsah, Život, Kariéra...

🔍 HLEDÁNÍ JMÉNA: 'Petr Rýdlo'
   ❌ Jméno 'Petr Rýdlo' nebylo na stránce nalezeno
   ℹ️  To je očekávané - demonstrace funkčnosti hledání
```

## Funkce
- Načítání HTML obsahu stránky
- Analýza všech typů odkazů
- Analýza struktury nadpisů
- Statistiky odstavců
- Hledání specifického jména v textu
- Identifikace nadřazeného elementu
- Export výsledků do JSON
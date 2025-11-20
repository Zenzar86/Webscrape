# Webscraper

Program pro webscraping veřejných stránek s hledaným jménem.

## Verze
- **webscraper.py** - Verze 1.0: Analyzuje jednu konkrétní stránku
- **webscraper_v2.py** - Verze 2.0: Vyhledává a analyzuje více stránek obsahujících hledané jméno

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

### Verze 1.0 (webscraper.py)
```bash
python3 webscraper.py
```
Analyzuje Wikipedii o Louisi de Funès a hledá jméno "Petr Rýdlo".

### Verze 2.0 (webscraper_v2.py) - DOPORUČENO
```bash
python3 webscraper_v2.py
```
Analyzuje skutečné stránky obsahující jméno "Petr Rýdlo":
- https://www.antikavion.cz/autor/petr-rydlo
- https://gask.art/ (Galerie - Zasloužilý umělec Petr Rýdlo)
- https://rejstrik-firem.kurzy.cz/

## Výstup
- **Verze 1.0**: Uloží výsledky do `webscraping_vysledky.json`
- **Verze 2.0**: Uloží výsledky do `webscraping_vysledky_v2.json`

## Příklad výstupu (Verze 2.0)
```
🌐 [2/3] STRÁNKA
📄 Analyzuji: https://gask.art/book/zaslouzily-umelec-petr-rydlo-obrazy-sklo/

📊 STATISTIKY:
   • Odkazy: 79 interních, 56 externích
   • Nadpisy: 12 celkem
   • Odstavce: 11

🎯 NALEZENO JMÉNO 'Petr Rýdlo':
   • Počet výskytů: 5

📌 První výskyt:
   • Tag: <div>
   • Nadřazený tag: <body>

📊 CELKOVÝ SOUHRN:
   • Analyzováno stránek: 3
   • Jméno nalezeno na: 1 stránkách
```

## Funkce
- Načítání HTML obsahu stránky
- Analýza všech typů odkazů
- Analýza struktury nadpisů
- Statistiky odstavců
- Hledání specifického jména v textu
- Identifikace nadřazeného elementu
- Export výsledků do JSON
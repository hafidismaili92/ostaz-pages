# -*- coding: utf-8 -*-
"""Génère les quatre versions linguistiques de la page de présentation.

    python _i18n/build.py

Source unique : _i18n/source.html (français). Sorties écrasées à chaque
exécution : index.html, en/index.html, es/index.html, ar/index.html.
Ne jamais éditer les sorties — elles sont regénérées.

Méthode : le HTML est parcouru nœud de texte par nœud de texte, et chaque
nœud est remplacé ENTIÈREMENT par sa traduction. Jamais de remplacement de
sous-chaîne : « Libre » ne peut donc pas corrompre « Don libre », et aucun
segment ne peut être traduit à l'intérieur du CSS, du JavaScript ou d'un SVG,
dont les plages sont exclues au préalable.

Tout segment français sans traduction est laissé en français ET signalé en
fin d'exécution, avec un code de sortie non nul. Ajouter du texte dans
source.html puis relancer suffit donc à savoir ce qui reste à traduire.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE = os.path.join(HERE, u'source.html')
STRINGS = os.path.join(HERE, u'strings.json')

# code : (chemin de sortie, direction, étiquette du sélecteur, URL)
# Ordre aligné sur le sélecteur des pages de suppression de compte, pour que
# les deux sélecteurs du site présentent les langues dans le même ordre.
LANGS = [
    (u'fr', u'index.html', u'ltr', u'FR', u'/'),
    (u'en', u'en/index.html', u'ltr', u'EN', u'/en/'),
    (u'es', u'es/index.html', u'ltr', u'ES', u'/es/'),
    (u'ar', u'ar/index.html', u'rtl', u'AR', u'/ar/'),
]

JUNK = re.compile(r'^[\s &;#0-9.,:/\-]*$')

# Pages écrites à la main qui existent dans les quatre langues, au même nom
# de fichier sous /en/, /es/ et /ar/. Toute nouvelle page légale traduite
# doit être ajoutée ici, sinon les versions étrangères de la page de
# présentation continueront de pointer vers le français.
LOCALISED_PAGES = [u'suppression-compte', u'confidentialite']

SITE = u'https://profkit.hafidonline.org'

# --- Sélecteur de langue -------------------------------------------------
# Le pied de page d'origine affichait quatre <span> inertes : un sélecteur
# qui n'en était pas. On le remplace en entier, ce qui rend l'opération
# idempotente — relancer le script ne l'empile pas.
SWITCHER_RE = re.compile(r'<div class="foot-langs">.*?</div>', re.S)
NAV_SWITCHER_RE = re.compile(r'<div class="nav-langs">.*?</div>', re.S)

FOOT_CSS_OLD = u'.foot-langs span{ cursor:default; }'
FOOT_CSS_NEW = (
    u'.foot-langs a{ color: rgb(var(--ink-faint)); text-decoration:none;'
    u' font-weight:700; transition: color .2s ease; }\n'
    u'.foot-langs a:hover{ color: rgb(var(--margin)); }\n'
    u'.foot-langs a[aria-current="page"]{ color: rgb(var(--margin)); }'
)

# --- Arabe ---------------------------------------------------------------
# Fraunces, Caveat et Source Serif 4 ne contiennent aucun glyphe arabe : sans
# substitution, la page tomberait sur la police serif par défaut du système.
# IBM Plex Sans Arabic est celle de l'application, d'où la continuité.
AR_HEAD = u"""<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* --- Arabe : police et miroir de la mise en page ------------------------
   Les sept règles ci-dessous sont les seules propriétés à direction
   physique de la feuille principale. Tout le reste est symétrique ou géré
   par flexbox, qui suit déjà `dir`. */
[dir="rtl"] body,
[dir="rtl"] h1, [dir="rtl"] h2, [dir="rtl"] h3, [dir="rtl"] h4,
[dir="rtl"] .hero-title, [dir="rtl"] .section-title,
[dir="rtl"] .price-amount, [dir="rtl"] .kicker, [dir="rtl"] .brand-name{
  font-family:'IBM Plex Sans Arabic', system-ui, 'Segoe UI', Tahoma, sans-serif;
}
[dir="rtl"] .nav-links a::after{ left:auto; right:0; }
[dir="rtl"] .hero-margin-rule{ left:auto; right:calc((100vw - 1180px)/2 + 128px); }
[dir="rtl"] .book-mock::before{ left:auto; right:0; }
[dir="rtl"] .float-card.grade{ right:auto; left:-10%; }
[dir="rtl"] .float-card.badge{ left:auto; right:-9%; }
[dir="rtl"] .feat-card .tag{ right:auto; left:22px; }
[dir="rtl"] .store-btn .stxt{ text-align:right; }
</style>
"""


def skip_ranges(html):
    """Plages à ne pas traduire : CSS, JavaScript, SVG, commentaires.

    Le sélecteur de langue en fait partie : ses étiquettes (FR, EN, AR, ES)
    sont des codes de langue, identiques dans toutes les versions, et le bloc
    entier est de toute façon régénéré plus bas. Sans cette exclusion elles
    seraient signalées comme « sans traduction » à chaque exécution.
    """
    out = []
    for tag in (u'script', u'style', u'svg'):
        for m in re.finditer(r'<' + tag + r'\b[^>]*>.*?</' + tag + r'>', html, re.S):
            out.append((m.start(), m.end()))
    for m in re.finditer(r'<!--.*?-->', html, re.S):
        out.append((m.start(), m.end()))
    for rx in (SWITCHER_RE, NAV_SWITCHER_RE):
        for m in rx.finditer(html):
            out.append((m.start(), m.end()))
    return out


def translate_text_nodes(html, lang, table, missing):
    skips = skip_ranges(html)

    def ignored(pos):
        return any(a <= pos < b for a, b in skips)

    pieces = []
    last = 0
    for m in re.finditer(r'>([^<>]+)<', html):
        raw = m.group(1)
        txt = raw.strip()
        # On teste la position du TEXTE (groupe 1), pas celle du '>' qui le
        # precede : ce '>' est le dernier caractere de la balise d'avant. Pour
        # un texte suivant un </svg> en ligne, il appartient encore a la plage
        # du SVG, et tester m.start() faisait silencieusement sauter le texte.
        # C'est exactement ce qui est arrive aux puces de l'offre, chacune
        # precedee d'une icone SVG.
        if not txt or JUNK.match(txt) or ignored(m.start(1)):
            continue
        entry = table.get(txt)
        tr = entry.get(lang) if entry else None
        if tr is None:
            missing.add(txt)
            continue
        head = raw[:raw.index(txt)]
        tail = raw[raw.index(txt) + len(txt):]
        pieces.append(html[last:m.start(1)])
        pieces.append(head + tr + tail)
        last = m.end(1)
    pieces.append(html[last:])
    return u''.join(pieces)


def translate_attrs(html, lang, table, missing):
    for fr, entry in table.items():
        tr = entry.get(lang)
        if tr is None:
            missing.add(fr)
            continue
        html = html.replace(u'"%s"' % fr, u'"%s"' % tr)
    return html


def build_switcher(active, css_class):
    """Les deux sélecteurs — en-tête et pied de page — sortent d'ici, donc
    ils ne peuvent pas diverger en ordre ni en destinations."""
    items = []
    for code, _out, _dir, label, url in LANGS:
        cur = u' aria-current="page"' if code == active else u''
        items.append(
            u'<a href="%s" hreflang="%s"%s>%s</a>' % (url, code, cur, label))
    return u'<div class="%s">%s</div>' % (css_class, u''.join(items))


def write_sitemap():
    """Écrit sitemap.xml, alternates hreflang compris.

    Généré plutôt que tenu à la main : chaque page ajoutée multiplie les URL
    par quatre et chaque URL porte cinq alternates. À 12 URL c'est déjà
    60 lignes qu'une main distraite désynchronise.
    """
    def urls_for(path_fr, paths):
        """paths : {code: url}. Retourne un bloc <url> par langue."""
        out = []
        for code, _o, _d, _l, _u in LANGS:
            alts = u''.join(
                u'\n    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>'
                % (c, SITE, paths[c]) for c, _o, _d, _l, _u in LANGS)
            alts += (u'\n    <xhtml:link rel="alternate" hreflang="x-default"'
                     u' href="%s%s"/>' % (SITE, path_fr))
            out.append(u'  <url>\n    <loc>%s%s</loc>%s\n  </url>'
                       % (SITE, paths[code], alts))
        return out

    blocks = []
    # Page de présentation : / , /en/ , /es/ , /ar/
    home = dict((c, u if c != u'fr' else u'/') for c, _o, _d, _l, u in LANGS)
    blocks += urls_for(u'/', home)
    # Pages légales : /slug , /en/slug , ...
    for slug in LOCALISED_PAGES:
        paths = {}
        for c, _o, _d, _l, _u in LANGS:
            paths[c] = u'/%s' % slug if c == u'fr' else u'/%s/%s' % (c, slug)
        blocks += urls_for(u'/%s' % slug, paths)

    xml = (u'<?xml version="1.0" encoding="UTF-8"?>\n'
           u'<!-- Généré par _i18n/build.py. Ne pas éditer à la main. -->\n'
           u'<urlset\n'
           u'  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           u'  xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + u'\n'.join(blocks) + u'\n</urlset>\n')
    io.open(os.path.join(ROOT, u'sitemap.xml'), 'w',
            encoding='utf-8', newline='\n').write(xml)
    return len(blocks)


def main():
    data = json.load(io.open(STRINGS, encoding='utf-8'))
    text_table = data[u'text']
    attr_table = data[u'attrs']
    source = io.open(SOURCE, encoding='utf-8').read()

    all_missing = {}
    for code, out_rel, direction, _label, _url in LANGS:
        html = source
        missing = set()

        if code != u'fr':
            html = translate_text_nodes(html, code, text_table, missing)
            html = translate_attrs(html, code, attr_table, missing)

        # Langue et direction du document
        html = re.sub(r'<html lang="[^"]*" dir="[^"]*">',
                      u'<html lang="%s" dir="%s">' % (code, direction), html, count=1)

        # Les pages légales existent dans les quatre langues : chaque version
        # doit pointer vers la sienne, pas vers la française. Oublier d'en
        # ajouter une ici enverrait un lecteur arabe sur du français.
        if code != u'fr':
            for slug in LOCALISED_PAGES:
                html = html.replace(u'href="/%s"' % slug,
                                    u'href="/%s/%s"' % (code, slug))

        # Les deux sélecteurs de langue : en-tête et pied de page
        html = NAV_SWITCHER_RE.sub(
            build_switcher(code, u'nav-langs'), html, count=1)
        html = SWITCHER_RE.sub(
            build_switcher(code, u'foot-langs'), html, count=1)
        html = html.replace(FOOT_CSS_OLD, FOOT_CSS_NEW)

        if direction == u'rtl':
            html = html.replace(u'</head>', AR_HEAD + u'</head>', 1)

        path = os.path.join(ROOT, out_rel)
        d = os.path.dirname(path)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        io.open(path, 'w', encoding='utf-8', newline='\n').write(html)

        print(u'  %-16s -> %-18s %d ko' % (code, out_rel, len(html) // 1024))
        if missing:
            all_missing[code] = missing

    n = write_sitemap()
    print(u'  %-16s -> %-18s %d URL' % (u'sitemap', u'sitemap.xml', n))

    if all_missing:
        print(u'\nSEGMENTS SANS TRADUCTION (laisses en francais) :')
        for code, segs in sorted(all_missing.items()):
            print(u'  [%s] %d' % (code, len(segs)))
            for s in sorted(segs):
                print(u'      %s' % s[:100])
        return 1

    print(u'\n  toutes les chaines sont traduites')
    return 0


if __name__ == '__main__':
    sys.exit(main())

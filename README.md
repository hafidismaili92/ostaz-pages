# ostaz-pages — site public de ProfKit

Dépôt servant les pages web de ProfKit via Cloudflare Pages. Il peut rester
privé : Cloudflare Pages se connecte aussi aux dépôts privés. Il ne contient
que du HTML statique — le code de l'application reste dans le dépôt `ostaz`.

## Arborescence

```
/_i18n/source.html              SOURCE de la présentation (FR) — la seule à éditer
/_i18n/strings.json             dictionnaire fr → en/es/ar
/_i18n/build.py                 générateur

/index.html                     présentation — FR   ┐
/en/index.html                  EN                  │ GÉNÉRÉS
/es/index.html                  ES                  │ ne pas éditer
/ar/index.html                  AR (RTL)            ┘

/suppression-compte.html        suppression de compte — FR (page par défaut)
/en/suppression-compte.html     EN                  ┐ écrits à la main,
/es/suppression-compte.html     ES                  │ une page par langue
/ar/suppression-compte.html     AR (RTL)            ┘
/assets/legal.css               feuille partagée par les quatre

/robots.txt                     exclut /_i18n/ de l'indexation
/sitemap.xml                    8 URL + alternates hreflang
```

Deux régimes, et c'est volontaire : la présentation est **générée** depuis une
source unique, parce que sa maquette de 84 Ko serait ingérable en quadruple.
Les pages de suppression sont **écrites à la main**, parce qu'une page à
portée légale doit pouvoir être relue mot à mot sans passer par un script.

Le nom de fichier est identique dans les quatre langues : le sélecteur de
langue est donc le même bloc dans chaque page, avec des chemins absolus
depuis la racine du site.

### Les URL servies n'ont pas d'extension

Cloudflare Pages **redirige `/x.html` vers `/x`** (307). Les liens internes
visent donc la forme sans extension, celle qui répond `200` directement :

```
https://profkit.hafidonline.org/suppression-compte
https://profkit.hafidonline.org/en/suppression-compte
https://profkit.hafidonline.org/es/suppression-compte
https://profkit.hafidonline.org/ar/suppression-compte
```

Les deux formes restent accessibles — la variante `.html` passe simplement
par une redirection. En ajoutant un lien, écrire la forme sans extension.

## La page de suppression de compte

C'est la seule page à portée légale : Google Play exige que la procédure soit
consultable **sans installer l'application**. URL à déclarer dans la Play
Console, section « Suppression des données » :

```
https://profkit.hafidonline.org/suppression-compte
```

Sans extension : c'est la forme qui répond `200`. Une fois déclarée, **ne
plus la renommer** — Google teste l'URL périodiquement, et une 404 sur la
procédure de suppression est un motif de suspension.

Les quatre langues reprennent celles de l'app (`src/i18n/locales/`). Les
libellés d'interface cités dans les instructions — « Réglages » /
« Settings » / « Ajustes » / « الإعدادات », et « Supprimer mon compte » /
« Delete my account » / « Eliminar mi cuenta » / « حذف حسابي » — sont copiés
**mot pour mot** depuis les fichiers de traduction de l'app. Un utilisateur
doit retrouver à l'écran exactement le mot qu'il lit ici. **Si un libellé
change dans l'app, il change ici aussi.**

Toute modification de fond doit être portée dans les **quatre** pages.

## Déploiement Cloudflare Pages

Aucune étape de build : ce sont des fichiers servis tels quels.

| Réglage | Valeur |
|---|---|
| Framework preset | *None* |
| Build command | *(vide)* |
| Build output directory | `/` |

Chaque `git push` sur la branche par défaut redéploie le site.

Le domaine `hafidonline.org` est déjà à toi : autant brancher un sous-domaine
(`profkit.hafidonline.org`) dans **Pages → Custom domains** plutôt que de
rester sur `.pages.dev`. Plus crédible sur une fiche Play, et surtout l'URL
déclarée à Google n'aura pas à changer ensuite.

## Adresse de contact

`profkit-contact@hafidonline.org` — posée dans les cinq pages, 17 occurrences
(lien `mailto:` et texte visible à chaque fois).

Adresse dédiée sur un domaine propre, et c'est volontaire : ces pages sont
publiques et indexées, l'adresse sera moissonnée par les robots de spam. Une
adresse dédiée se filtre, se redirige ou se remplace sans toucher à une boîte
personnelle.

Elle sert aussi de contact pour la politique de confidentialité (C-02), les
CGU (C-08) et le contact développeur de la Play Console — qui est **affiché
publiquement** sur la fiche de l'app.

## La page de présentation

### Modifier le texte

Tout se passe dans `_i18n/` :

1. écrire le **français** dans `_i18n/source.html` ;
2. `python _i18n/build.py` ;
3. le script liste les segments sans traduction et **sort en erreur** — les
   ajouter dans `_i18n/strings.json`, puis relancer.

Un texte non traduit reste en français plutôt que de disparaître : la page
est toujours lisible, et l'oubli est signalé au lieu d'être silencieux. Le
script est idempotent, on peut le relancer sans crainte.

Les clés de `strings.json` sont le **texte français exact**, entités
comprises (`&amp;`). Le générateur remplace des **nœuds de texte entiers**,
jamais des sous-chaînes : « Libre » ne peut donc pas corrompre « Don libre »,
et rien ne peut être traduit à l'intérieur du CSS, du JavaScript ou d'un SVG.

### L'arabe

`ar/index.html` reçoit en plus, injecté par le générateur :

- **IBM Plex Sans Arabic**, celle de l'application. Fraunces, Caveat et
  Source Serif 4 ne contiennent aucun glyphe arabe : sans substitution, la
  page tomberait sur la police serif par défaut du système.
- **sept règles `[dir="rtl"]`** qui inversent les seules propriétés à
  direction physique de la feuille principale (soulignés du menu, filet de
  marge, cartes flottantes, étiquettes des fonctionnalités, boutons de
  téléchargement). Tout le reste est symétrique ou géré par flexbox, qui suit
  déjà `dir`.

### Origine

La source provient de `landing/index-free.html` du dépôt applicatif — la
variante **sans offre Premium**. C'est celle qui décrit la réalité de l'app :
`monetization_mode` vaut `free` par défaut et aucune intégration de paiement
n'existe. L'autre variante (Premium à 29 DH/mois) n'est volontairement pas
publiée : annoncer un abonnement qu'on ne peut pas souscrire est un motif de
retrait Play.

### Liens encore inactifs dans `index.html`

Laissés en `href="#"`, car ils dépendent de travaux en cours (voir
`documentation/backlog-conformite.md` du dépôt applicatif) :

- **Confidentialité** et **Conditions d'utilisation** — entrées C-02 et C-08.
  La politique de confidentialité est un **bloquant Play** : son URL est
  obligatoire dans la Play Console. À écrire avant publication, et elle devra
  elle aussi être multilingue, puisqu'elle a une portée légale.
- **Boutons App Store / Google Play / version web** — à remplir quand les
  fiches existeront. Aucune app iOS n'est prévue à ce jour.
- **Centre d'aide**, **Guide de démarrage**, **Nouveautés** — pages non
  écrites. Les retirer si elles ne viennent pas : un lien mort sur un site
  public dessert plus qu'un lien absent.

### `hreflang`

Non posé, faute de domaine connu : les balises `<link rel="alternate"
hreflang>` demandent des URL absolues. À ajouter dans les quatre pages une
fois le domaine arrêté. Le sélecteur de langue visible suffit pour les
utilisateurs ; `hreflang` ne sert qu'au référencement.

## Source

Ces fichiers ont été initialisés depuis `ostaz/landing/`. Depuis la mise en
place des quatre langues, **ce dépôt est la source de vérité** pour les pages
de suppression de compte : `ostaz/landing/suppression-compte.html` n'est plus
qu'un vestige de la version française monolingue et ne doit plus être édité.

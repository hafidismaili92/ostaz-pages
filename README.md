# ostaz-pages — site public de ProfKit

Dépôt servant les pages web de ProfKit via Cloudflare Pages. Il peut rester
privé : Cloudflare Pages se connecte aussi aux dépôts privés. Il ne contient
que du HTML statique — le code de l'application reste dans le dépôt `ostaz`.

## Arborescence

```
/index.html                     présentation (français uniquement)
/suppression-compte.html        suppression de compte — FR (page par défaut)
/en/suppression-compte.html     EN
/es/suppression-compte.html     ES
/ar/suppression-compte.html     AR (RTL)
/assets/legal.css               feuille partagée par les quatre
```

Le nom de fichier est identique dans les quatre langues : le sélecteur de
langue est donc le même bloc dans chaque page, avec des chemins absolus
depuis la racine du site.

## La page de suppression de compte

C'est la seule page à portée légale : Google Play exige que la procédure soit
consultable **sans installer l'application**. Son URL se déclare dans la Play
Console, section « Suppression des données » :

```
https://<domaine>/suppression-compte.html
```

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

## Travaux restants

### `index.html` n'existe qu'en français

L'app est en quatre langues, la page de présentation en une seule. Ce n'est
pas bloquant pour publier — Google n'exige rien sur la langue de la page de
présentation — mais c'est incohérent pour un lancement international.

Traduire 86 Ko de texte commercial est un travail de contenu, pas de code.
Deux approches, à choisir avant de commencer :

1. **Quatre fichiers statiques**, comme la page de suppression. Robuste et
   bon pour le référencement, mais la copie commerciale évolue souvent et
   chaque retouche devra être faite quatre fois.
2. **Une page et un dictionnaire de traductions** chargé en JavaScript
   (attributs `data-i18n`). Une seule page à maintenir, au prix d'un contenu
   dépendant du JS — acceptable pour du marketing, à éviter pour du légal.

`index.html` provient de `landing/index-free.html` du dépôt applicatif — la
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

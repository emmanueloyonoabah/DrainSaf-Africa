# DrainSaf Africa — Guide pas à pas

## 0. Contenu du projet

```
Projet 2 PJ/
├── app.py                 ← point d'entrée Streamlit
├── requirements.txt       ← streamlit, pandas, numpy, plotly
├── GUIDE.md               ← ce guide
├── .streamlit/config.toml ← thème clair + options
├── drainsaf/
│   ├── config.py          ← référentiels, barèmes, palette
│   ├── data.py            ← CSV, score de gravité, priorisation, données démo
│   ├── auth.py            ← connexion par rôles (st.session_state)
│   ├── ui.py              ← CSS (thème SaaS) et composants
│   ├── charts.py          ← graphiques Plotly
│   └── views.py           ← pages (connexion, saisie, tableaux de bord)
└── data/inspections.csv   ← créé automatiquement au 1er lancement
```

**Comptes de démonstration**

| Rôle | Identifiant | Mot de passe |
|---|---|---|
| Inspecteur Terrain | `inspecteur1` | `Inspect2025` |
| Inspecteur Terrain | `inspecteur2` | `Inspect2026` |
| Ingénieur Municipal / Administrateur | `ingenieur` | `Drain2025` |

---

## 1. Lancer l'application en local (Windows)

Prérequis : [Python 3.10+](https://www.python.org/downloads/) (cocher « Add Python to PATH » à l'installation).

Ouvrez un terminal dans le dossier du projet, puis :

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Le navigateur s'ouvre sur `http://localhost:8501`. Au premier lancement, un jeu de **données de démonstration** (18 ouvrages à Douala et Yaoundé, 42 inspections) est créé dans `data/inspections.csv`.
Pour l'enlever : connectez-vous en ingénieur → onglet **Exports & données** → **Administration des données**.

> Sur macOS / Linux, l'activation est `source .venv/bin/activate`.

---

## 2. Créer un dépôt GitHub et y pousser le code

1. Créez un compte sur <https://github.com> si besoin, puis installez [Git](https://git-scm.com/downloads).
2. Sur GitHub : **New repository** → nom `drainsaf-africa` → *Public* (nécessaire pour la formule gratuite de Streamlit Cloud) → **Create repository** (ne cochez pas « Add a README »).
3. Dans le terminal, à la racine du projet :

```bash
git init
```

```bash
git add .
```

```bash
git commit -m "DrainSaf Africa : première version"
```

```bash
git branch -M main
```

```bash
git remote add origin https://github.com/VOTRE-UTILISATEUR/drainsaf-africa.git
```

```bash
git push -u origin main
```

(GitHub demande une authentification : utilisez GitHub Desktop, ou un *Personal Access Token* en guise de mot de passe.)

Le fichier `.gitignore` exclut déjà `data/inspections.csv` et `.streamlit/secrets.toml` : vos données locales et vos secrets ne partent pas sur GitHub.

---

## 3. Déployer gratuitement sur Streamlit Community Cloud

1. Allez sur <https://share.streamlit.io> et connectez-vous avec votre compte **GitHub** (autorisez l'accès à vos dépôts).
2. Cliquez sur **Create app** → **Deploy a public app from GitHub**.
3. Renseignez :
   - **Repository** : `VOTRE-UTILISATEUR/drainsaf-africa`
   - **Branch** : `main`
   - **Main file path** : `app.py`
   - (facultatif) **App URL** : choisissez un nom, ex. `drainsaf-africa`
4. Cliquez sur **Deploy**. Après 1 à 3 minutes d'installation, l'application est en ligne sur `https://drainsaf-africa.streamlit.app` : partagez ce lien avec vos camarades et le jury.
5. Chaque `git push` sur `main` redéploie automatiquement l'application.

### Remplacer les comptes de démonstration (recommandé en ligne)

Dans Streamlit Cloud : **Settings → Secrets**, collez (et adaptez) :

```toml
[users.m_etoundi]
name = "Ing. Marie Etoundi"
role = "ingenieur"          # ou "inspecteur"
password_sha256 = "COLLER_LE_HASH_ICI"

[users.j_kamga]
name = "Jean-Paul Kamga"
role = "inspecteur"
password_sha256 = "COLLER_LE_HASH_ICI"
```

Pour générer le hash d'un mot de passe :

```bash
python -c "import hashlib; print(hashlib.sha256('MonMotDePasse'.encode()).hexdigest())"
```

Dès que `[users]` existe dans les secrets, les comptes de démonstration sont désactivés (mettez aussi `DEMO_HINTS = []` dans `drainsaf/auth.py` pour masquer l'aide de connexion).

### Limite à connaître : stockage éphémère

Streamlit Community Cloud **ne conserve pas les fichiers écrits** : le CSV est réinitialisé quand l'application redémarre (inactivité, redéploiement). C'est parfait pour la démonstration devant le jury (les données démo sont régénérées), mais pour une vraie exploitation il faudrait une base persistante (Google Sheets, Supabase, PostgreSQL…). Téléchargez régulièrement l'historique depuis l'onglet **Exports & données**.

---

## 4. Règles métier (pour votre rapport)

**Score de gravité /100** = obstruction (5 / 12 / 21 / 30) + état structurel (0 / 12 / 25) + déchets majeurs (0 / 10) + criticité déclarée (5 / 18 / 35).

| État | Condition | Priorité | Délai |
|---|---|---|---|
| 🔴 Critique | criticité « Urgent / Critique » **ou** score ≥ 65 | P1 · Immédiate | ≤ 72 h |
| 🟠 Alerte | criticité « Modéré » **ou** score ≥ 35 | P2 · Court terme | ≤ 15 jours |
| 🟢 Sain | sinon | P3 · Veille | ≤ 60 jours |

- **Indice de vulnérabilité du réseau** = ouvrages à l'état *Critique* ÷ ouvrages suivis (dernière inspection de chaque ouvrage ; un ouvrage = ville + quartier + rue + type + repère).
- **Bandeau d'alerte** : ouvrages dont la dernière inspection porte la criticité « Urgent / Critique » (risque d'inondation imminent).
- **Action et équipe recommandées** : déduites de l'obstruction, de l'état structurel, des déchets et du type d'ouvrage (curage manuel / mécanique / hydrocureur, réparation de fissures, réhabilitation, équipe mixte…).

Les barèmes se règlent dans `drainsaf/config.py`.

# Financial Time Machine

Voyez l'effet d'une décision financière **avant** de la prendre.

Vous décrivez un projet (voiture, logement, travaux, études, mariage) et l'application montre
votre épargne mois par mois, avec et sans ce projet, sur 3 à 10 ans. Elle compare plusieurs
façons de le réaliser, teste votre résistance à un coup dur et note votre santé financière.

![Dashboard](docs/dashboard.png)

## Fonctionnalités

- **Projection What-If** : chaque modification recalcule instantanément les deux futurs possibles.
- **Comparaison de scénarios** : acheter maintenant, dans 6 ou 12 mois, ou moins cher, avec une recommandation justifiée.
- **Stress test** : perte d'emploi de 3 ou 6 mois, baisse de revenu de 30 %.
- **Financial Health Score** : une note sur 100, expliquée facteur par facteur.
- **Avertissements** : apport supérieur à l'épargne, crédit au-delà de 40 % du revenu, frais anormaux.
- **Historique** : enregistrer, comparer et rouvrir ses simulations.

## Lancer le projet

Seul prérequis : [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
git clone https://github.com/houssembalbali1234/financial-time-machine.git
cd financial-time-machine
cp .env.example .env        # sous Windows : copy .env.example .env
docker compose up -d --build
```

| Service | Adresse |
| --- | --- |
| Dashboard | http://localhost:3000 |
| API et documentation interactive | http://localhost:8000/docs |
| PostgreSQL | localhost:5433 |

## Architecture

```
Navigateur ──► Frontend Next.js (port 3000)
                    │
                    ▼
               API FastAPI (port 8000) ──► Moteur de simulation (Python pur)
                    │
                    ▼
               PostgreSQL 16 (historique)
```

Le **moteur de simulation** ne dépend ni du web ni de la base de données : il peut être
réutilisé tel quel, par exemple intégré dans l'application d'une banque.

## Stack

| Partie | Technologies |
| --- | --- |
| Backend | Python 3.13, FastAPI, Pydantic, SQLAlchemy, pytest |
| Frontend | Next.js 16, React, TypeScript, Tailwind CSS, Recharts |
| Données | PostgreSQL 16 |
| Infrastructure | Docker, Docker Compose |

## Développement

```bash
# Base de données seule
docker compose up -d db

# Backend (rechargement automatique)
cd backend
python -m venv .venv
.venv\Scripts\activate       # Linux / macOS : source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (dans un autre terminal)
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
python -m pytest
```

50 tests couvrent le moteur de calcul, l'API et l'historique.

## Feuille de route

- [x] Moteur de simulation, scénarios, stress test, Health Score
- [x] Dashboard What-If
- [x] Historique avec PostgreSQL et Docker
- [ ] Comptes utilisateurs
- [ ] Prévisions par machine learning
- [ ] Assistant IA et « Lettre du futur »

## Avertissement

Outil de simulation à but éducatif. Il ne constitue pas un conseil financier ou d'investissement.
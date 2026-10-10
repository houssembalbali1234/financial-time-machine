# Financial Time Machine

Voyez l'effet d'une décision financière **avant** de la prendre.

Vous décrivez un projet (voiture, logement, travaux, études, mariage) et l'application montre
votre épargne mois par mois, avec et sans ce projet, sur 3 à 10 ans. Elle compare plusieurs
façons de le réaliser, teste votre résistance à un coup dur, note votre santé financière, et une
IA locale (Llama) vous explique le résultat en langage simple.

![Dashboard](docs/dashboard.png)

## Fonctionnalités

- **Projection What-If** : chaque modification recalcule instantanément les deux futurs possibles.
- **Comparaison de scénarios** : acheter maintenant, dans 6 ou 12 mois, ou moins cher, avec une recommandation justifiée.
- **Stress test** : perte d'emploi de 3 ou 6 mois, baisse de revenu de 30 %.
- **Financial Health Score** : une note sur 100, expliquée facteur par facteur.
- **Avertissements** : apport supérieur à l'épargne, crédit au-delà de 40 % du revenu, frais anormaux.
- **Comptes et historique** : chaque utilisateur enregistre et rouvre ses simulations.
- **Lettre du futur** : une lettre de « vous dans 3 ans », écrite par l'IA à partir de vos chiffres.
- **Assistant financier** : posez vos questions (« Et si j'attendais un an ? ») en langage naturel.

## Une IA contrôlée

L'IA (Llama 3.1, servie par Ollama) tourne **en local** : aucune donnée financière ne quitte le
serveur. Elle ne calcule jamais rien :

1. le moteur de simulation calcule tous les chiffres ;
2. le code fixe l'interprétation (« situation tendue mais sous contrôle ») ;
3. Llama rédige le texte à partir de ces seuls éléments ;
4. le code **vérifie** la réponse : chiffres clés présents, aucun montant inventé, ton adapté.
   En cas de problème, il redemande une version corrigée, puis signale à l'utilisateur ce qui reste douteux.

## Lancer le projet

Seul prérequis : [Docker Desktop](https://www.docker.com/products/docker-desktop/) (8 Go de RAM conseillés pour l'IA).

```bash
git clone https://github.com/houssembalbali1234/financial-time-machine.git
cd financial-time-machine
cp .env.example .env        # sous Windows : copy .env.example .env, puis remplissez les valeurs
docker compose up -d --build
docker compose exec ollama ollama pull llama3.1:8b    # une seule fois, environ 5 Go
```

| Service | Adresse |
| --- | --- |
| Dashboard | http://localhost:3000 |
| API et documentation interactive | http://localhost:8000/docs |
| PostgreSQL | localhost:5433 |
| Ollama (Llama) | localhost:11434 |

## Architecture

```
Navigateur ──► Frontend Next.js (port 3000)
                    │
                    ▼
               API FastAPI (port 8000) ──► Moteur de simulation (Python pur)
                    │            │
                    ▼            ▼
          PostgreSQL 16     Ollama + Llama 3.1 (IA locale)
     (comptes, historique)
```

Le **moteur de simulation** ne dépend ni du web, ni de la base de données, ni de l'IA : il peut
être réutilisé tel quel, par exemple intégré dans l'application d'une banque.

## Stack

| Partie | Technologies |
| --- | --- |
| Backend | Python 3.13, FastAPI, Pydantic, SQLAlchemy, pytest |
| Sécurité | Mots de passe Argon2, jetons JWT |
| Frontend | Next.js 16, React, TypeScript, Tailwind CSS, Recharts |
| IA | Llama 3.1 8B, Ollama |
| Données | PostgreSQL 16 |
| Infrastructure | Docker, Docker Compose, GitHub Actions |

## Développement

```bash
# Base de données et IA seules
docker compose up -d db ollama

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

79 tests couvrent le moteur de calcul, l'API, les comptes, l'historique et l'IA (avec un faux
Llama, pour des tests rapides et sans dépendance). Ils sont relancés automatiquement par GitHub
Actions à chaque envoi de code.

## Feuille de route

- [x] Moteur de simulation, scénarios, stress test, Health Score
- [x] Dashboard What-If et avertissements
- [x] Comptes utilisateurs et historique avec PostgreSQL
- [x] Docker Compose et intégration continue
- [x] Lettre du futur et assistant financier avec Llama, réponses vérifiées
- [ ] Prévisions par machine learning sur l'historique de dépenses
- [ ] Interface en arabe et en anglais
- [ ] Mise en ligne

## Avertissement

Outil de simulation à but éducatif. Il ne constitue pas un conseil financier ou d'investissement.
# Learning Streak Builder - Site Web

Site web vitrine pour le bot Discord Learning Streak Builder.

## Déploiement sur Railway

Ce site est configuré pour être déployé sur Railway.app avec un domaine gratuit.

### Déploiement automatique

1. Pousse le code sur GitHub
2. Connecte-toi sur [Railway.app](https://railway.app)
3. Crée un nouveau projet et sélectionne ce dossier `website`
4. Railway détectera automatiquement la configuration
5. Ton site sera disponible sur un domaine gratuit `*.railway.app`

### Technologies

- HTML5
- CSS3 (Design moderne avec animations)
- JavaScript vanilla
- Python (serveur HTTP pour Railway)

### Domaine personnalisé (optionnel)

Tu peux aussi configurer un domaine personnalisé gratuit via :
- Freenom (domaines .tk, .ml, .ga, .cf, .gq)
- Connecter ton domaine dans les settings Railway

## Développement local

```bash
cd website
python -m http.server 8000
```

Puis ouvre http://localhost:8000

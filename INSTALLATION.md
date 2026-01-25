# Installation rapide - Parkings Strasbourg

## Étape 1 : Copier les fichiers

Copiez tout le dossier `strasbourg_parkings` dans :

```
/config/custom_components/strasbourg_parkings/
```

Structure finale :
```
/config/
  └── custom_components/
      └── strasbourg_parkings/
          ├── __init__.py
          ├── config_flow.py
          ├── const.py
          ├── manifest.json
          ├── sensor.py
          ├── strings.json
          ├── translations/
          │   ├── en.json
          │   └── fr.json
          └── README.md
```

## Étape 2 : Redémarrer Home Assistant

Allez dans **Paramètres** → **Système** → **Redémarrer**

## Étape 3 : Ajouter l'intégration

1. **Paramètres** → **Appareils et services**
2. Cliquez sur **+ Ajouter une intégration** (bouton en bas à droite)
3. Recherchez "**Strasbourg Parkings**"
4. Sélectionnez les parkings qui vous intéressent
5. Cliquez sur **Valider**

## Étape 4 : Vérifier

Les capteurs sont créés avec le format :
- `sensor.gutenberg`
- `sensor.opera_broglie`
- `sensor.austerlitz`
- etc.

## Parkings disponibles

**Centre-ville :**
- Austerlitz
- Bateliers  
- Opéra Broglie
- Gutenberg
- Kléber Homme de Fer
- Saint-Nicolas

**Les Halles :**
- Halles P1 Marais Vert
- Halles P2 Sébastopol
- Halles P3 Wilson

**Autres :**
- Centre Historique Petite France
- Rivétoile Cinéma
- Rivétoile Commerces
- Esplanade
- Danube Bleu
- Gare Wodli
- Sainte-Aurélie Gare

## Utilisation

Chaque capteur affiche le **nombre de places disponibles** et contient ces attributs :
- `occupation` : Places occupées
- `capacite_totale` : Total de places
- `taux_occupation` : Pourcentage (%)
- `statut` : Ouvert/Fermé
- `nom_complet` : Nom du parking

## Exemple de carte dashboard

```yaml
type: entities
title: Mes Parkings
entities:
  - sensor.gutenberg
  - sensor.opera_broglie
  - sensor.austerlitz
```

## Problèmes ?

Vérifiez les logs : **Paramètres** → **Système** → **Logs**

Cherchez les erreurs contenant "strasbourg_parkings"

# Strasbourg Parkings - Intégration Home Assistant

Intégration custom pour Home Assistant permettant de suivre en temps réel la disponibilité des places de parking à Strasbourg.

## Fonctionnalités

- ✅ Configuration via l'interface utilisateur (UI)
- ✅ Sélection multiple des parkings à surveiller
- ✅ Mise à jour automatique toutes les 3 minutes
- ✅ 16 parkings disponibles dans Strasbourg et ses environs
- ✅ Attributs détaillés : occupation, capacité, taux d'occupation, statut

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

**Quartiers :**
- Centre Historique Petite France
- Rivétoile Cinéma
- Rivétoile Commerces
- Esplanade
- Danube Bleu

**Gare :**
- Gare Wodli
- Sainte-Aurélie Gare

## Installation

### Méthode 1 : Installation manuelle

1. Copiez le dossier `strasbourg_parkings` dans le répertoire `custom_components` de votre installation Home Assistant :

```bash
/config/custom_components/strasbourg_parkings/
```

2. Redémarrez Home Assistant

3. Allez dans **Paramètres** → **Appareils et services** → **+ Ajouter une intégration**

4. Recherchez "Strasbourg Parkings"

5. Sélectionnez les parkings que vous souhaitez surveiller

### Méthode 2 : Via HACS (si vous publiez l'intégration sur GitHub)

1. Ajoutez ce repository comme repository custom dans HACS
2. Installez "Strasbourg Parkings"
3. Redémarrez Home Assistant
4. Configurez via l'UI

## Configuration

### Depuis l'interface utilisateur

1. **Paramètres** → **Appareils et services** → **+ Ajouter une intégration**
2. Recherchez "Strasbourg Parkings"
3. Cochez les parkings que vous souhaitez surveiller
4. Cliquez sur "Valider"

### Capteurs créés

Pour chaque parking sélectionné, un capteur est créé avec :

**État principal :** Nombre de places disponibles

**Attributs :**
- `occupation` : Nombre de places occupées
- `capacite_totale` : Nombre total de places
- `taux_occupation` : Pourcentage d'occupation (%)
- `statut` : Ouvert / Fermé
- `nom_complet` : Nom complet du parking
- `parking_id` : Identifiant technique

## Exemples d'utilisation

### Carte simple

```yaml
type: entities
title: Parkings Strasbourg
entities:
  - entity: sensor.gutenberg
    secondary_info: last-changed
  - entity: sensor.opera_broglie
  - entity: sensor.austerlitz
```

### Carte avec template

```yaml
type: markdown
content: |
  ## Places disponibles
  
  **Gutenberg:** {{ states('sensor.gutenberg') }} places
  ({{ state_attr('sensor.gutenberg', 'taux_occupation') }}% occupé)
  
  **Broglie:** {{ states('sensor.opera_broglie') }} places
  ({{ state_attr('sensor.opera_broglie', 'taux_occupation') }}% occupé)
```

### Automation : Alerte si peu de places

```yaml
automation:
  - alias: "Alerte parking presque plein"
    trigger:
      - platform: numeric_state
        entity_id: sensor.gutenberg
        below: 10
    action:
      - service: notify.mobile_app
        data:
          message: "Attention : il ne reste que {{ states('sensor.gutenberg') }} places au parking Gutenberg"
```

### Template sensor : Meilleur parking disponible

```yaml
template:
  - sensor:
      - name: "Meilleur parking centre-ville"
        state: >
          {% set parkings = [
            ('sensor.gutenberg', 'Gutenberg'),
            ('sensor.opera_broglie', 'Broglie'),
            ('sensor.austerlitz', 'Austerlitz')
          ] %}
          {% set available = namespace(max=0, name='') %}
          {% for entity, name in parkings %}
            {% set places = states(entity) | int(0) %}
            {% if places > available.max %}
              {% set available.max = places %}
              {% set available.name = name %}
            {% endif %}
          {% endfor %}
          {{ available.name }}
        attributes:
          places_disponibles: >
            {% set parkings = [
              'sensor.gutenberg',
              'sensor.opera_broglie',
              'sensor.austerlitz'
            ] %}
            {% set available = namespace(max=0) %}
            {% for entity in parkings %}
              {% set places = states(entity) | int(0) %}
              {% if places > available.max %}
                {% set available.max = places %}
              {% endif %}
            {% endfor %}
            {{ available.max }}
```

## Source des données

Les données proviennent de l'API Open Data de l'Eurométropole de Strasbourg :
- URL : https://data.strasbourg.eu
- Dataset : occupation-parkings-temps-reel
- Fréquence de mise à jour : Toutes les 3 minutes

## Support

Pour toute question ou problème :
1. Vérifiez les logs de Home Assistant
2. Ouvrez une issue sur GitHub
3. Vérifiez que l'API de Strasbourg est accessible

## Licence

MIT License

## Crédits

Données fournies par l'Eurométropole de Strasbourg via leur plateforme Open Data.

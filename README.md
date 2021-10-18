# Mediapart Daily PDF to Remarkable

Récupère le PDF des articles de la journée précédente et les envoie vers votre liseuse ReMarkable

## Fonctionnement

Une GitHub action tourne tous les jours à 6h du matin et lance un script Python qui télécharge la version PDF du journal de la veille, et l'uploade sur votre ReMarkable Cloud.

Vous avez besoin d'un compte abonné Mediapart

## Installation locale

```sh
poetry install
```

## Récupération initiale du Remarkable Device Token

La première fois, vous devez récupérer un token d'identification unique de 7 caractères depuis Remarkable à cette adresse : [my.remarkable.com/device/browser/connect](https://my.remarkable.com/device/browser/connect)

Puis lancez cette commande:

```sh
poetry run python scripts/get_device_token.py
```

## Usage local

```sh
M2M_MEDIAPART_LOGIN=your@address.com \
M2M_MEDIAPART_PASSWORD=yourpassword \
M2M_REMARKABLE_DEVICE_TOKEN=longjwt.token.fromremarkable \
poetry run python -m m2m.run
```

## Usage automatisé depuis GitHub actions

- forkez ce repo
- créez les 3 secrets dans les settings du repo
- c'est tout :)

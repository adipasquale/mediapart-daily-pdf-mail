# Mediapart Daily PDF Mail

Récupère le PDF des articles de la journée précédente et les envoie à une adresse mail

## Fonctionnement

Une GitHub action tourne tous les jours à 6h du matin et lance un script Python qui télécharge la version PDF du journal de la veille, et l'envoie par email.

Vous avez besoin d'un compte abonné Mediapart et d'identifiants à un serveur SMTP pour l'envoi de mail.

Un cas d'usage pratique est de le combiner avec [Remailable](https://remailable.getneutrality.org/) pour recevoir le PDF sur votre liseuse Remarkable.

## Usage

```sh
M2M_MEDIAPART_LOGIN=your@address.com \
M2M_MEDIAPART_PASSWORD=yourpassword \
M2M_SMTP_SERVER_HOST=smtp.yourprovider.com \
M2M_SMTP_FROM_EMAIL=your@address.com \
M2M_SMTP_PASSWORD=yourSMTPpassword \
M2M_SMTP_TO_EMAIL=destination@email.com \
poetry run python -m m2m.run
```


## Développement

```sh
poetry install
```

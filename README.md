# vanced-apk-updater

Controlla ogni 6 ore se su LeeAPK ci sono nuove versioni di **YouTube Vanced**
e **YouTube Music Premium**. Quando trova un aggiornamento, scarica gli APK e
li invia come documenti WhatsApp al gruppo "Distribuzione di app" tramite
OpenWA (motore Baileys), che gira direttamente sul runner di GitHub Actions.

## Come funziona

1. `scripts/check_apks.py` legge le pagine LeeAPK, estrae versione/build e il
   link diretto all'APK, e confronta con `state.json`.
2. Se ci sono novità, il workflow scarica gli APK, avvia OpenWA sul runner,
   ripristina la sessione WhatsApp dal secret e invia i file al gruppo.
3. `state.json` viene aggiornato e committato, così ogni versione viene
   inviata una sola volta.

## Secrets richiesti

| Nome | Contenuto |
|---|---|
| `OPENWA_API_KEY` | Chiave API di OpenWA |
| `OPENWA_BAILEYS_CREDS_B64` | `creds.json` Baileys in base64 (sessione WhatsApp) |
| `WA_GROUP_ID` | ID del gruppo WhatsApp destinatario |

Se la sessione scade (il job fallisce con "rigenerare il secret"),
rifare il pairing e aggiornare `OPENWA_BAILEYS_CREDS_B64`.

# Telegram-DiscordWebhook

Reenvía mensajes de Telegram (grupos, canales, usuarios) a un espacio de Discord
usando webhooks. Desarrollado con
[Telethon](https://github.com/LonamiWebs/Telethon) y
[aiohttp](https://github.com/aio-libs/aiohttp). Requiere Python 3.8 o superior.

- Reenvía archivos adjuntos siempre que no superen el tamaño indicado en
  `config.json`.
- Añade la imagen del chat como imagen de perfil del webhook de Discord.

## Instalación

1. Clonar el repositorio

    ```bash
    git clone https://github.com/CrysoK/telegram-discordwebhook
    cd telegram-discordwebhook

2. Crear un "entorno virtual" (opcional)

    ```bash
    python -m venv .venv
    # activarlo en Linux
    source .venv/bin/activate
    # activarlo en Windows (cmd)
    .venv\Scripts\activate
    # activarlo en Windows (powershell)
    .venv/Scripts/Activate.ps1
    ```

3. Instalar dependencias

    ```bash
    pip install -r requirements.txt
    ```

4. Renombra `sample.config.json` a `config.json` y define los valores necesarios

    - `api_id` y `api_hash` se obtienen [aquí](https://my.telegram.org/)
    - `ibb_key` (opcional) se obtiene de [ImgBB](https://api.imgbb.com/) y
      permite que el mensaje de Discord tenga la imagen del chat de Telegram.
    - `max_size`: tamaño máximo de los archivos a reenviar (en MB).
    - `pphoto_expiration`: tiempo de expiración de las imágenes subidas a
      [ImgBB](https://imgbb.com/) (en dias).
    - `webhooks`: diccionario donde las claves son los IDs de los chats de
      Telegram y los valores son la URL de los webhooks de Discord. La clave `*`
      equivale a todos los chats. [¿Cómo obtener el ID y la URL?](#ids-y-urls)

## Uso

Para ejecutar el programa simplemente ejecuta:

```bash
python main.py
```

### IDs y URLs

El argumento `-l`, `--list`, permite mostrar los IDs de los chats accesibles por la cuenta de Telegram.

Para obtener URL del webhook de Discord sigue [estos
pasos](https://support.discord.com/hc/es/articles/228383668-Introducci%C3%B3n-a-los-webhook).

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

4. Renombra `sample.config.json` a `config.json` y define la configuración:

    - `api_id` y `api_hash` se obtienen [aquí](https://my.telegram.org/).
    - `ibb_key` (opcional) se obtiene de [ImgBB](https://api.imgbb.com/) y
      permite que el mensaje de Discord tenga la imagen del chat de Telegram.
    - `ibb_expiration` (opcional) indica el tiempo de expiración de las imágenes
      subidas a [ImgBB](https://imgbb.com/) (en dias). Por defecto es 7.
    - `max_size` (opcional) es el tamaño máximo de los archivos a reenviar (en
      MB). Por defecto es 10 MB.
    - `chats`: diccionario donde las claves son los IDs de los chats de Telegram
      y los valores la configuración individual. La clave `*` equivale a
      "todos".

      - `comment` (opcional) permite identificar los chats con algún comentario.
      - `ignore_users` (opcional) es una lista de usuarios cuyos mensajes no se
        reenviarán.
      - `webhooks` es una lista de URLs de webhook de Discord.

## Uso

Para iniciar el programa simplemente ejecuta:

```bash
python main.py
```

**Importante**: la primera vez se solicitarán los siguientes datos:

- Número de teléfono
- Código de inicio de sesión
- Contraseña (si aplica)

### IDs y URLs

El argumento `-l`, `--list`, permite mostrar los IDs de los chats accesibles por la cuenta de Telegram.

Para obtener la URL de un webhook de Discord sigue [estos
pasos](https://support.discord.com/hc/es/articles/228383668-Introducci%C3%B3n-a-los-webhook).

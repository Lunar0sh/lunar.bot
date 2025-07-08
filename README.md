# Lunar.bot

## Lunar.bot is a Discord bot that automatically fetches and posts NASA's Astronomy Picture of the Day (APOD) to designated channels across multiple servers.

### Features

  * **Daily APOD Posts**: Automatically posts the new Picture of the Day at a set time.
  * **Manual Fetching**: Admins can use a slash command (`/apod`) to post the current APOD at any time.
  * **Multi-Server Support**: Can be configured to post in a specific channel on any server it's invited to.
  * **Image Caching & Processing**:
      * Fetches the APOD from NASA only once per day to stay within API limits.
      * Downloads the image, resizes it to a web-friendly size, and converts it to PNG format to ensure it always displays correctly in Discord.
      * Caches the original and converted images locally in `/cached_raw` and `/cache` directories.
  * **Robust Error Handling**: Gracefully handles large images by posting a link instead of a file, and correctly formats posts for both images and videos.

-----

### Setup

Follow these steps to get the bot running.

#### 1\. Prerequisites

  * Python 3.8 or newer.
  * A Discord Bot Token.
  * A NASA API Key.

#### 2\. Installation

  * **Clone the repository or download the files:**
    Get the `bot.py`, `requirements.txt`, and this `README.md` file and place them in a new project folder.
  * **Install dependencies:**
    Open your terminal or command prompt, navigate to your project folder, and run:
    ```bash
    pip install -r requirements.txt
    ```
  * **Create the environment file:**
    Create a new file in the same directory named `.env`. Open it and add your secret keys, replacing the placeholders with your actual credentials:
    ```env
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
    NASA_API_KEY=YOUR_NASA_API_KEY_HERE
    ```

-----

### 3\. Running the Bot

Once the setup is complete, you can start the bot by running the following command in your terminal from the project directory:

```bash
python bot.py
```

-----

### 4\. Inviting the Bot

To add your bot to a Discord server, you need to create an invitation link.

1.  Go to the Discord Developer Portal and select your application.
2.  Navigate to the **OAuth2 \> URL Generator** page.
3.  In the **SCOPES** section, select `bot` and `applications.commands`.
4.  In the **BOT PERMISSIONS** section that appears, select the following permissions:
      * `Send Messages`
      * `Read Message History`
      * `Embed Links`
      * `Attach Files`
      * `Use Slash Commands`
5.  Copy the generated URL at the bottom of the page.
6.  Paste the URL into your web browser and select the server you wish to add the bot to. You must have administrative permissions on that server.

-----

### Usage

lunar.space uses slash commands for configuration.

  * `/set_channel`
    Sets the current channel for daily APOD posts. You must have "Administrator" permission to use this command.
  * `/unset_channel`
    Stops the bot from sending daily APOD posts to this server. You must have "Administrator" permission to use this command.
  * `/apod`
    Manually fetches and posts the current APOD. You must have "Administrator" permission to use this command.

-----

**Bot by lunar\_sh**

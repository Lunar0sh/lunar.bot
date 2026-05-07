# Privacy Policy for Lunar.bot (APOD Bot)

Last Updated: May 7, 2026

This Privacy Policy explains how Lunar.bot ("the Bot", "we", "our") collects, uses, and protects your information when you use the Bot within Discord.

## 1. Information We Collect
To provide its core functionality, the Bot collects and stores the following minimum required data:
* **Guild (Server) IDs and Channel IDs:** When an administrator uses the `/apod_setup` command, the Bot saves the ID of the server and the ID of the designated channel to a local configuration file to deliver the daily Astronomy Picture of the Day.
* **Command Interactions:** We temporarily log command executions (e.g., who executed `/apod`) in our local console logs for diagnostic and debugging purposes.

**We do NOT collect or store:**
* Message content (what you type in chat).
* Personal user data (names, email addresses, etc.).
* Voice data or media uploaded by users.

## 2. How We Use Your Information
The collected data is used exclusively for the following purposes:
* To schedule and deliver automated daily APOD messages to the configured channels.
* To respond to user commands (e.g., `/apod`, `/random`).
* To maintain the health, stability, and performance of the Bot (via diagnostic logs).

## 3. Data Storage and Retention
* **Configuration Data:** Server and Channel IDs are stored in a local JSON file. This data is kept as long as the Bot is configured to post in your server. You can overwrite this data at any time by using the `/apod_setup` command again, or you can request its deletion by kicking the Bot from your server.
* **NASA Media Cache:** The Bot temporarily downloads and caches images and videos directly from the NASA API to respect API rate limits. This cache contains no user data and is automatically purged every 7 days.

## 4. Third-Party Services
The Bot interacts with the following third-party services:
* **Discord API:** To function within the Discord ecosystem.
* **NASA API (api.nasa.gov):** To fetch the daily astronomical images, videos, and descriptions. No user data is sent to NASA.

## 5. Your Rights
If you are a Server Administrator, you have the right to request the deletion of your server's configuration data at any time by removing the Bot from your server and contacting the developer.

## 6. Contact
For any questions, data deletion requests, or support regarding this Privacy Policy, please contact the developer via Discord: `Lunar_sh`.
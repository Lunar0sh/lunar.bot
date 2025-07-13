### **Privacy Policy for Lunar.bot**

**Last Updated:** July 13, 2025

This Privacy Policy describes how the Discord bot "Lunar.bot" collects, uses, and stores data. By adding this bot to your Discord server, you agree to the practices described in this policy.

#### **1. What Data We Collect**

The bot is designed to function with a minimal amount of data. The only information that is actively stored is:

* **Server ID (Guild ID):** When an administrator uses the `/set_channel` command, the unique ID of the Discord server (Guild) is saved.
* **Channel ID:** Along with the Server ID, the ID of the channel designated for daily APOD posts is saved.

This information is stored locally in a file named `apod_channels.json` on the system where the bot is hosted.

The bot **does not** collect or store:
* User content such as messages (other than the command invocations themselves).
* Personal information about users, such as usernames, email addresses, or Discord tags.
* Information about other channels or server categories.

#### **2. How We Use Data**

The stored Server and Channel IDs are used exclusively for the bot's core functionality:

* **Daily Posts:** To automatically post the daily Astronomy Picture of the Day (APOD) to the designated channel.
* **Functionality:** The bot requires this information to know on which servers and in which channels it should be active.

The bot interacts with the **NASA API** to retrieve APOD data. No personal or server-specific data is transmitted to NASA during this process.

#### **3. Data Storage and Security**

* **Local Storage:** The configuration file (`apod_channels.json`) is stored locally on the machine running the bot. The security of this file is the responsibility of the person hosting the bot.
* **Image Caching:** The bot downloads images from NASA and temporarily stores them in the `/cache` and `/cached_raw` directories. This is for performance improvement and to comply with NASA's API rate limits. These images do not contain any user or server data.

#### **4. Data Sharing**

We do not share any of the data we store (Server and Channel IDs) with third parties.

#### **5. Your Rights and Control**

You have full control over the data related to your server:

* **Data Deletion:** You can remove the data stored for your server at any time by using the `/unset_channel` command. This will delete your server's entry from the `apod_channels.json` file.
* **Removing the Bot:** If you remove the bot from your server, it will no longer be able to access any data or post in your server.

#### **6. Changes to This Policy**

This Privacy Policy may be updated to reflect future changes to the bot. We recommend reviewing it periodically.

#### **7. Contact**

The bot is developed and maintained by **lunar_sh**. For any questions regarding this Privacy Policy, please contact the developer.

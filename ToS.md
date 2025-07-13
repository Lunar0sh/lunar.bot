### **Terms of Service for Lunar.bot**

**Last Updated:** July 13, 2025

These Terms of Service ("Terms") govern your use of the Discord bot "Lunar.bot" ("Bot"). By adding the Bot to your Discord server or using it, you agree to these Terms.

#### **1. Services Provided**

* The Bot automatically fetches NASA's daily "Astronomy Picture of the Day" (APOD) and posts it to a designated channel.
* The service includes both automated daily posts and the ability for administrators to manually fetch the current APOD using the `/apod` command.
* The Bot processes and converts images to ensure compatibility with Discord and caches them temporarily.

#### **2. User Responsibilities**

* **Administrators:** To use the configuration commands (`/set_channel`, `/unset_channel`, `/apod`), you must have administrator permissions on the respective Discord server.
* **Hosting (if applicable):** If you are hosting the Bot yourself, you are responsible for:
    * Obtaining and securely storing your own credentials, including a Discord Bot Token and a NASA API Key, in an `.env` file.
    * Installing the necessary dependencies as listed in the `requirements.txt` file.
    * Providing a suitable runtime environment (Python 3.8 or newer).

#### **3. Acceptable Use**

* You agree to use the Bot only for its intended purpose, which is displaying content from the NASA Astronomy Picture of the Day.
* You are not permitted to misuse the Bot, disrupt its function, or attempt to access its configuration outside of the provided commands.
* The use of administrative commands is strictly limited to users with the appropriate permissions on the server.

#### **4. Third-Party Services**

* The Bot's functionality depends on the availability of third-party services, specifically the **Discord API** and the **NASA API**.
* The developer of the Bot has no control over the availability or terms of these external services. Outages or changes in these services may impact the Bot's functionality.

#### **5. Disclaimer of Warranties**

* The Bot is provided "as is" and "as available".
* No guarantee is made for the uninterrupted, error-free, or secure operation of the Bot. The Bot may fail to retrieve the APOD if the NASA API is unreachable, or image processing may fail.

#### **6. Limitation of Liability**

The developer of the Bot (**lunar_sh**) is not liable for any direct or indirect damages arising from the use or inability to use the Bot. This includes damages from operational interruptions or loss of data. If you host the Bot yourself, you are solely responsible for the security of your API keys.

#### **7. Termination of Use**

* You can terminate the use of the service on your server at any time by executing the `/unset_channel` command to stop daily posts or by removing the Bot from your server.
* The developer reserves the right to cease development and support for the Bot at any time.

#### **8. Changes to the Terms**

These Terms may be changed at any time. It is your responsibility to review the Terms periodically. Continued use of the Bot after a change constitutes acceptance of the new Terms.

#### **9. Contact**

For questions about these Terms of Service, please contact the developer, **lunar_sh**.

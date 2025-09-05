# 📘 Satisfactory Discord Bot – Documentation

## 1. Overview
The **Satisfactory Discord Bot** integrates a dedicated Satisfactory server with your Discord community.  

### Current Features
- Configure server connection through a Discord modal (channel, server address, ports, passwords).  
- Display server status (online/offline, player count, session details).  
- Automatic updates in a designated Discord channel.  

This bot provides a convenient way to manage and monitor your game server without leaving Discord.

---

## 2. Setup Guide

### Requirements
- Python 3.10+  
- Discord Bot Application (created via [Discord Developer Portal](https://discord.com/developers/applications))  
- A running Satisfactory dedicated server  

### Installation(Local)
1. Clone the repository:
   ```bash
   git clone https://github.com/mangddung/satisfactory-discord-bot.git
   cd satisfactory-discord-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_discord_bot_token
   ```

4. Start the bot:
   ```bash
   python main.py
   ```

### Installation(Docker)
1. Clone the repository:
   ```bash
   git clone https://github.com/mangddung/satisfactory-discord-bot.git
   cd satisfactory-discord-bot
   ```
   
2. Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_discord_bot_token
   ```

3. Start with Docker Compose:
   ```bash
   docker-compose up -d
   ```
---

## 3. Bot Permissions

When registering your bot in the **Discord Developer Portal**, configure the correct permissions.

- **Permission Integer**: `2147576848`  
- This grants the bot rights for:
  - Managing channels
  - View Channels
  - Sending/Manage messages
  - Embed Links
  - Read Message History
  - Using slash commands  

<img width="1178" height="781" alt="image" src="https://github.com/user-attachments/assets/fe51f6cb-1c7d-408d-ad54-764262c23621" />

---

## 4. Future Features (Planned)
- **Server Status Channel Enhancements**  
  Display active users and their roles in the server status message.  

- **Docker Integration**  
  Connect with a Dockerized Satisfactory server to allow commands such as:  
  - Start/Stop server  
  - Restart server  
  - Fetch logs  

- **Role-based Access Control**  
  Restrict server control commands to specific roles (e.g., Admin, Moderator).  

---

✅ With this setup, your bot will already be functional for monitoring your server.  
🚀 In future updates, it will evolve into a full server management tool directly from Discord.

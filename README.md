# 📘 Satisfactory Discord Bot – Documentation

## 1. Overview
The **Satisfactory Discord Bot** integrates a dedicated Satisfactory server with your Discord community.

### Features
- Configure server connection through a Discord modal (channel, server address, ports, passwords).
- Display server status (online/offline, player count, session details) with automatic periodic updates.
- Connect a Dockerized Satisfactory server and control it directly from Discord.
- Role-based and member-based access control for server start/stop commands.

---

## 2. Setup Guide

### Requirements
- Python 3.10+
- Discord Bot Application (created via [Discord Developer Portal](https://discord.com/developers/applications))
- A running Satisfactory dedicated server

### Installation (Local)
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
   BOT_PREFIX=!
   BOT_STATUS_MESSAGE=Online
   SERVER_CHECK_INTERVAL=60
   CONTAINER_ID=your_docker_container_id
   ```
   > `CONTAINER_ID` is optional. If omitted, Docker control commands are disabled.

4. Start the bot:
   ```bash
   python main.py
   ```

### Installation (Docker)
1. Clone the repository:
   ```bash
   git clone https://github.com/mangddung/satisfactory-discord-bot.git
   cd satisfactory-discord-bot
   ```

2. Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_discord_bot_token
   CONTAINER_ID=your_docker_container_id
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

## 4. Slash Commands

### Server Monitoring

| Command | Permission | Description |
|---------|------------|-------------|
| `/initial-setup` | Administrator | Opens a modal to register a Satisfactory server. Creates a dedicated status channel and starts periodic updates. |

### Privilege Management

| Command | Permission | Description |
|---------|------------|-------------|
| `/add-member` | Administrator + Channel Owner | Grant a specific member start/stop permission for a channel. |
| `/add-role` | Administrator + Channel Owner | Grant a Discord role start/stop permission for a channel. All members with that role are affected. |

### Docker Control

> Requires `CONTAINER_ID` to be set in `.env` and Docker to be running.

| Command | Permission | Description |
|---------|------------|-------------|
| `/connect-docker` | Administrator + Channel Owner | Bind the configured Docker container to a server status channel. |
| `/disconnect-docker` | Administrator + Channel Owner | Unbind the Docker container from its channel. |
| `/server-start` | Privileged member or role | Start the Satisfactory Docker container. |

---

## 5. Privilege System

Server control commands (`/server-start`) are protected by a per-channel privilege system.

- Privileges are set per channel using `/add-member` or `/add-role`.
- **Member privilege**: grants access to a specific user by Discord user ID.
- **Role privilege**: grants access to all members who hold a specific Discord role.
- Each privilege entry independently controls `can_start` and `can_stop`.
- Privilege checks evaluate member privileges first, then role privileges.

---

## 6. Workflow

```
1. /initial-setup
   └─ Creates a status channel → starts periodic server status updates

2. /connect-docker  (optional, requires CONTAINER_ID in .env)
   └─ Links the Docker container to the status channel

3. /add-member  or  /add-role
   └─ Grants start/stop control to a user or role

4. /server-start
   └─ Starts the server (privilege checked automatically)
```

# PartyKit Relay Setup Guide

## What is PartyKit?

PartyKit (partykit.io) is a free WebSocket hosting service that lets you create real-time apps. We'll use it as a relay server so host and client can communicate through it.

## Step 1: Sign Up for PartyKit

1. Go to https://partykit.io
2. Click "Sign Up" or "Get Started"
3. Sign up with GitHub or Email (free, no credit card)
4. Install the PartyKit CLI:
   ```bash
   npm install -g partykit
   ```

## Step 2: Deploy the Relay Server

1. Open terminal/command prompt
2. Navigate to this folder:
   ```bash
   cd /path/to/NeverScam
   ```
3. Login to PartyKit:
   ```bash
   partykit login
   ```
4. Deploy your relay:
   ```bash
   partykit deploy
   ```

5. **Copy your relay URL!** It will look like:
   ```
   https://neverscam-relay.username.partykit.dev
   ```
   You'll need this URL for the host and client.

## Step 3: Configure Host

Edit `silent-install.py` and change the relay URL:

```python
RELAY_URL = "https://neverscam-relay.username.partykit.dev"
```

Then rebuild the installer:
```bash
build-installer.bat
```

## Step 4: Configure Client

Edit `main.py` and add the relay URL option:

```python
# In the connection dialog, add a field for relay URL
# Or hardcode it:
RELAY_URL = "https://neverscam-relay.username.partykit.dev"
```

## Step 5: Test

1. **On host computer:**
   - Run `NeverScamInstaller.exe` (silent, no windows)

2. **On client computer:**
   - Run `main.py`
   - Select "Relay Mode" or enter relay URL
   - Connect to host

## How It Works

```
[Host] ──WebSocket──> [PartyKit Relay] <──WebSocket── [Client]
                  neverscam-relay.username.partykit.dev

1. Host connects to PartyKit and waits
2. Client connects to same PartyKit
3. PartyKit routes messages between them
```

## Troubleshooting

**Connection failed:**
- Check PartyKit URL is correct in both host and client
- Verify PartyKit server is deployed: `partykit dev`

**Host not appearing:**
- Check PartyKit dashboard for connections
- Host must be running with relay enabled

**Client can't find host:**
- Both must connect to same PartyKit room
- Check firewalls allow outgoing WebSocket connections

## Cost

- PartyKit free tier: Generous limits for personal use
- No credit card required
- Should work well for 1-2 simultaneous connections


## Help Content

**Title:** Managing Integrations
**Format:** Help article
**Audience:** All
**Slug:** managing-integrations
**Purpose:** View, reconnect, and troubleshoot your connected apps in App Center.

**Content:**

Connected apps need occasional management. Tokens expire. Permissions change. This article covers how to keep your integrations running smoothly.

### Viewing Connected Apps

Open App Center from the sidebar. Each integration card shows its connection status:

- **Connected** (green badge) — The integration is active and working.
- **Not Connected** (gray outline) — No active connection. Click "Connect" to set it up.
- **Coming Soon** (gray badge) — Coming in a future release.
- **Error** (red badge) — The connection has a problem that needs attention.

### Reconnecting an App

If a connection stops working (red Error badge):

1. Open App Center and find the affected app.
2. Click "Manage" or "Reconnect."
3. You are prompted to re-authenticate with the third-party service.
4. Sign in and grant permissions again.

Common reasons for connection failure:

- The third-party password changed.
- The third-party updated its API permissions.
- The authorization token expired (most tokens expire after a set period).
- You revoked access from the third-party's side.

### Disconnecting an App

1. Open App Center and find the app.
2. Click "Manage" or "Disconnect."
3. Confirm the disconnection.

The app is removed from your account. Platform features tied to it disappear. Data already synced to the third-party service is not deleted.

### Troubleshooting Connection Issues

**App shows "Error" status.**
Click "Reconnect." If the problem persists, check that the third-party service is online and your account there is active.

**App shows "Connected" but does not appear to work.**
Disconnect and reconnect the integration. If the issue continues, check that the app is configured correctly in the third-party service's settings.

**Auth prompt loops or does not complete.**
Clear your browser cache and cookies. Try a different browser. Disable ad blockers that may interfere with the auth redirect.

**Connected app missing expected data.**
Check the sync status. Some apps sync periodically rather than in real-time. Wait a few minutes or use a manual sync option if available.

### Managing Multiple Connections

You can connect multiple apps in the same category. For example, both ChatGPT and Gemini can be connected simultaneously. Each connection is managed independently.

### Security

- App connections use OAuth or similar secure authorization protocols.
- ReiSearch does not store your third-party passwords.
- You can revoke access at any time from either ReiSearch or the third-party service.

**Next steps:**
- What Is the App Center?
- How to Connect and Use CRM Integrations
- Using AI Integrations
- App Center FAQs

**Status:** Draft v0.1

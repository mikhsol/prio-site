Prio gives you direct controls for deleting app-owned data. You do not need to
submit a request to delete the data stored by Prio on your device.

> **Use Delete All Data before uninstalling when possible.** On iOS,
> device-only Keychain items can survive uninstall. Remote copies held by a
> service you chose also require that service's deletion controls.

## Delete app-owned data inside Prio

### Android

1. Open **Prio**.
2. Open **More**.
3. Choose **Backup & Export**.
4. Under **Danger zone**, choose **Delete all data**.
5. Review the warning and confirm.

This clears app-owned tasks, goals, briefings, settings, local backups, and
saved remote-provider API keys on the device, then returns Prio to its first-run
state.

### iOS

Open Prio's settings and choose **Delete All Data** from the backup and data
controls. The operation clears core records, local backups, provider
credentials, the explicit-cloud-backup key, stale exports, chats and analyses,
downloaded models, notifications, and settings. If a category fails, Prio
reports the failed category instead of claiming complete deletion so you can
retry.

## Delete individual records or credentials

You can delete tasks, goals, and other supported records individually. Remove a
remote-provider API key with that provider's remove control when you no longer
want it stored by Prio.

## Clear or uninstall the app

On Android, you can clear Prio's storage through **Android Settings > Apps >
Prio > Storage & cache > Clear storage**. Uninstalling removes the app's local
Android data.

On iOS, uninstalling removes the app container but may not remove device-only
Keychain items. Use Prio's in-app **Delete All Data** control first if you want
those app-owned credentials and keys removed.

## Data held by another service

Deleting local Prio data cannot erase a copy already received by another
service:

| Destination | What to do |
|---|---|
| Google Drive backup | Delete Prio's private app data through Google controls and remove Prio's access in your Google Account. Disconnecting inside Prio only stops future backup attempts. |
| Firebase Analytics or Crashlytics | Turning either independent diagnostics toggle off stops future collection. Google controls retention of records already uploaded. |
| OpenAI, Anthropic, Google Gemini, or xAI | Remove the API key in Prio to stop future requests, then use the selected provider's account and deletion process for data already sent. |
| Clipboard, export, share destination, assistant, or paired client | Clear or delete the copy using the receiving app, device, or service controls. |
| Google Play or Apple App Store | Use the store account and privacy controls for historical entitlement, transaction, or review records. |

## Contact

For help with Prio's deletion controls or data deliberately sent to Prio
support, email **mik.prio.ai@gmail.com** with the subject
**Data Deletion Request**.

Prio does not operate an application server that stores your task database.
For data held by Google, Apple, an AI provider, or another destination you
selected, use that provider's privacy and deletion process.

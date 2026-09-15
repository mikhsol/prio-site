Prio is a privacy-first task and planning app for Android and iOS. Core task
capture, goals, reminders, prioritization, and rule-first classification run on
your device. You do not need a Prio account for core use.

Some features use third-party services or a destination you choose. This policy
explains when data leaves your device, who receives it, what they receive, how
to stop future transfers, and whether Prio can read it.

## 1. Data stored on your device

Prio stores information you enter or create, which may include:

- tasks, notes, priorities, dates, tags, goals, and progress;
- local calendar-derived records and meeting or briefing summaries;
- settings, notification preferences, AI-provider configuration, and local chat
  history;
- locally downloaded AI models; and
- local JSON backups and exports you create.

Prio uses this data locally to provide app features. Local records remain until
you delete them, clear app data, or uninstall the app, subject to platform
backup and Keychain behavior described below.

## 2. AI processing

### Rule-first and on-device AI

Automatic task classification starts with deterministic rules. When supported
and selected, Gemini Nano, Apple Foundation Models, or a downloaded llama.cpp
model runs on the device. Task content does not leave the device for these
operations. After AI is enabled, Android may automatically request the Gemini
Nano component when the on-device fallback reaches Nano. Downloaded llama.cpp
models remain an explicit choice. These download flows are described in
Section 7.

Quick Capture voice input requires Android or iOS on-device speech recognition.
Prio does not fall back to a cloud-capable recognizer for audio or transcript
processing.

### Android direct remote providers

On Android, you can opt in to a remote provider and supply your own API key.
When you select that provider and send a request, Prio sends the API key in an
HTTPS header and sends the system instruction, selected prompt, retained
eligible conversation history, provider/model identifier, and ordinary network
metadata directly to OpenAI, Anthropic, Google Gemini, or xAI. The history has
no count limit and can include partial assistant output that remains in the
local transcript. There is no Prio proxy.

The selected provider can read the plaintext request and controls its retention
under your provider account, settings, and agreement. Prio's operator does not
receive a server copy. Remove the credential, disable the provider, or choose
an on-device model to stop future requests. Deleting data in Prio does not
delete data already received by the provider.

The reviewed iOS build stores provider configuration and credentials but does
not directly execute remote-provider chat requests.

### External-AI planning and sharing

Android and iOS can build a planning prompt from content you select. Prio shows
the plaintext payload and warning before you copy it or open the system share
sheet. If you continue, the clipboard and the app or service you choose may
receive task, goal, My Day, calendar, date, note, priority, and planning text.

Prio reads the data locally to build the preview. The Prio operator receives no
copy unless you deliberately choose a Prio-controlled destination. After
handoff, the recipient controls access, retention, and deletion. Clear the
clipboard and use the recipient's controls to remove its copy.

## 3. Firebase analytics and crash diagnostics

Prio release builds can use Google Firebase, but Analytics and Crashlytics are
each off by default and independent: enabling one does not enable the other.
Once you independently enable a toggle, Firebase may process app interactions,
sessions, crash stack traces, diagnostics, app version, device/OS metadata, a
Firebase installation/device identifier, and IP address. Firebase Analytics can
derive coarse geography from IP data; Crashlytics is not the evidenced source
of approximate location.

Firebase can associate events with the same app installation or device. Not
requiring a Prio account does not make this data anonymous.

Prio does not intentionally put task text, notes, email, or other user content
into analytics or crash logs. Prio does not request or use advertising
identifiers, serve ads, or use Firebase data for cross-app tracking.

- **Android Analytics:** off until you enable **Experimental features** under
  **More > AI & Advanced > AI & Smart Features**, then opt in under
  **More > AI & Advanced > AI health diagnostics**.
- **Android Crashlytics:** off until you opt in, independently of Analytics,
  on that same **AI health diagnostics** screen.
- **iOS Analytics and Crashlytics:** off until you independently opt in to
  either under **Settings > Privacy Policy > Diagnostics sharing**.
- **Debug builds:** collection is disabled by the reviewed platform policies.

Turning Analytics off stops future Analytics collection. Crash reporting
withdrawal completes after restarting Prio and clearing unsent reports; until
then, the change can remain pending. Neither action deletes reports already
received by Google. Google controls provider retention. People authorized to
access Prio's Firebase project can view analytics reports and crash diagnostics.

### Android diagnostic exports

For Android only, we may use Firebase's daily batch export to copy
Crashlytics reports and Firebase session data into a restricted Google
BigQuery dataset in the EU for stability analysis. These copies can contain
raw stack traces and installation/session identifiers; they are not anonymous
aggregates. This does not enable Analytics, streaming, or iOS exports, or
change your in-app consent settings. The EU location applies to the BigQuery
copy, not the original Firebase processing.

In the current BigQuery Sandbox, tables, views, and partitions automatically
expire after 60 days. Authorized project administrators can delete these
resources earlier. Stopping collection or unlinking the export does not erase
existing copies. Google may retain recovery copies under its retention rules;
resource expiration is not a promise of immediate erasure of every copy.

## 4. Provider credentials

- **Android:** API credentials are stored in Keystore-backed encrypted
  preferences.
- **iOS:** API credentials are stored in the Keychain with device-only
  `AfterFirstUnlock` accessibility.

Credentials are not sent to Prio's operator. Android sends a credential only to
the remote provider you selected when you make a remote request. The reviewed
iOS build does not use stored credentials for direct provider requests.

Use the per-provider remove control to delete a credential. The shipped iOS
settings also expose **Delete All Data**, which removes all provider
credentials, the explicit-cloud-backup encryption key, core local records,
local backups, and other app-owned data. If any target fails, iOS identifies
the failed category instead of claiming complete deletion.

## 5. Backup, restore, and export

### Android

Android system Auto Backup is disabled. If you opt in to Google Drive backup:

- Prio requests Google authorization for only `drive.appdata` (private app-data)
  access. This grants permission to use Drive, not a Prio account sign-in;
  Prio does not request or receive your Google account email or profile;
- Prio uploads to Drive's private `appDataFolder`;
- the backup payload is encrypted with AES-256-GCM before upload;
- Google can see OAuth authorization, network, file, size, time, and ciphertext
  metadata but cannot read the encrypted task payload without the local Prio
  key; and
- Prio retains up to three usable remote backups and prunes backups older than
  72 hours while preserving the newest or known-good copy.

**Disconnect** stops future backup attempts in Prio, but it does not revoke
Google access or remove existing Drive copies. Remove Prio's access in Google
Account settings to revoke authorization, and delete Drive app data through
Google controls to remove remote copies. Google may retain service records
under its policy.

### iOS

iCloud backup controls are visible in Settings. Availability requires the app's
iCloud capability, an available iCloud account and container, network access,
and your explicit opt-in. When available and enabled, Prio encrypts a local
backup with AES-256-GCM before sending it to app-specific storage in your iCloud
account. Prio sends encrypted contents and backup metadata, not the locally
stored decryption key. Apple operates that storage; the Prio operator receives
no backup copy.

Disconnecting stops future backup attempts; it does not delete copies already
in iCloud. Remove remote copies using the available Prio backup-deletion
controls or your iCloud storage controls.

Prio stores its internal database and generated local JSON backups under
app-private Application Support, marks those roots and files excluded from
Apple-managed backup, and applies Data Protection that permits access after the
device's first unlock. Generated local JSON backups remain readable to the app
rather than separately encrypted as files.

### Manual export

A full export is plaintext JSON and may contain most app records. It leaves the
device only when you choose a share or storage destination. The selected app or
service can read and retain it. Delete both the local export and destination
copy when no longer needed.

## 6. Store entitlement checks and all-features-free mode

All Prio features are currently free. Prio does not offer a paid plan or new
purchase while this mode is active.

For compatibility with earlier purchases, Android can query Google Play at cold
startup when cached-tier revalidation is due or when you request a restore. iOS
starts a StoreKit transaction listener and entitlement refresh during
initialization, refreshes on foreground entry, and may load product metadata on
relevant settings screens. Google or Apple receives app/product, store account,
device, and network metadata. Prio receives entitlement status, not
payment-card details. The store provider controls transaction retention.

## 7. Other off-device flows

| Flow | Trigger and recipient | Data and control |
|---|---|---|
| On-device model component/download | After AI is enabled, Android may request the Gemini Nano component; downloaded llama.cpp models remain user-selected. | Google AI Core/Play services or the allowlisted model host receives component/model and network metadata, not task content. |
| Connected agent (Android) | You start and pair a localhost/USB-forwarded session. | A paired client can receive the fixed read-only scope over pinned HTTPS/TLS. Sessions expire within 15 minutes; the client controls any retained copy. |
| Siri/Shortcuts or Android App Actions | You invoke an OS assistant or automation. | The requested task, goal, count, proposal, or briefing result is returned to the OS surface. |
| Support and website links | You tap a link or send a message. | The browser or mail provider receives destination, network metadata, and content you choose to send. |
| Store rating | Prio asks the platform review API whether to show a prompt after eligible task completion. | The store receives app/store and network metadata, not task content. Review text is handled only if you submit it. |

## 8. Data sale, advertising, and tracking

Prio does not sell personal data, serve third-party advertising, or use data for
cross-app advertising tracking. This does not mean the app makes no network
connections: Firebase, store entitlement checks, model downloads, opt-in
backup, direct remote AI, and user-directed sharing operate as described above.

## 9. Deletion and retention

You can delete individual records on both platforms. Android and iOS also
expose **Delete All Data** controls for app-owned local data. On iOS, the
operation clears Room records, local backups, provider credentials, the
explicit iCloud backup key, stale exports, chats and analyses, downloaded
models, notifications, and settings. It reports partial failure or cancellation
without claiming success.

Device-only Keychain items can survive uninstall if you uninstall without first
using the app's deletion controls.

Deletion on the device cannot erase data already sent to Firebase, an AI
provider, Google Drive, Apple or Google stores, an assistant, a paired client,
the clipboard, or a share recipient. Use each recipient's account and deletion
controls. For a deletion request concerning the private Android BigQuery
diagnostic copy described in Section 3, contact Prio below.

## 10. Security

Prio uses platform storage protections, HTTPS for Internet transfers,
Keystore/Keychain-backed secrets, and AES-256-GCM for explicit cloud-backup
payloads. No system can guarantee absolute security. Protect your device,
provider accounts, API keys, exports, and backup destinations.

## 11. Children

Prio is not directed to children under 13 and does not knowingly create Prio
accounts or collect children's data through a Prio server. Platform and
third-party services used at a guardian's direction remain subject to their own
terms.

## 12. Changes and contact

We may update this policy when shipped behavior or legal requirements change.
The last-updated date above will reflect material changes.

Send privacy questions, requests concerning the private BigQuery diagnostic
copy, or requests about data sent directly to Prio support to
**mik.prio.ai@gmail.com**. For other data held by Google, Apple, an AI provider,
or another share recipient, use that provider's privacy and deletion process.

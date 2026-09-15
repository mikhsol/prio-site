These Terms govern your use of the Prio Android and iOS applications. By using
Prio, you agree to these Terms and the [Privacy Policy](/privacy-policy.html). If you
do not agree, do not use Prio.

## 1. The service

Prio is a task, goal, planning, reminder, and AI-assistance application. Core
features work without a Prio account. Some optional features use your platform
account, an AI-provider account, or another app or service you choose.

Prio provides prioritization and planning assistance, not professional,
medical, legal, financial, or emergency advice. You remain responsible for
reviewing outputs and deciding what action to take.

## 2. All-features-free mode

All currently shipped Prio features are available without a new purchase. Prio
does not currently offer a paid plan or purchase.

Google Play Billing and Apple StoreKit compatibility remain in the apps to
validate historical entitlements. Store providers may process product,
transaction, account, device, and network metadata even though no new purchase
is offered. If paid functionality is introduced later, it will require updated
in-app terms, store disclosures, prices, and purchase consent before it is
offered. These Terms do not authorize an undisclosed charge.

## 3. Your content and device

You retain ownership of tasks, notes, goals, prompts, exports, and other content
you create. You grant Prio only the local permissions needed to process that
content for features you request.

You are responsible for:

- safeguarding your device, backups, exports, API credentials, and provider
  accounts;
- ensuring content you enter or share is lawful and does not violate another
  person's rights;
- reviewing reminders, dates, classifications, and AI output before relying on
  them; and
- maintaining independent copies of information you cannot afford to lose.

## 4. AI features

Automatic classification is rule-first and may use an on-device model when one
is available. AI output can be inaccurate, incomplete, or unsuitable.

On Android, if you configure and select a remote AI provider, Prio sends your
API credential, selected prompt, retained eligible conversation history,
system instruction, and model request directly to that provider over HTTPS.
That history is not count-limited and can include partial assistant output that
remains in the local transcript. The provider's terms, fees, quotas, and
retention apply. Prio does not proxy the request, operate the provider, or
control provider-side deletion.

On Android and iOS, external-AI planning lets you preview and then copy or share
a plaintext prompt to an app or service you select. You authorize that transfer
when you continue from the preview. Once transferred, the recipient's terms and
privacy practices apply.

Do not submit content to an external AI provider unless you have the right to
do so. Do not use AI output as the sole basis for decisions that could
materially affect a person's rights, safety, health, employment, credit, or
legal position.

## 5. Credentials and third-party accounts

API credentials are stored with Android Keystore-backed encrypted preferences
or iOS Keychain protections. You are responsible for credentials you provide,
provider charges they incur, and revoking compromised keys. Prio's operator
does not receive your keys through a Prio server.

Google Drive backup, Apple services, Firebase, model hosts, app stores, system
assistants, connected-agent clients, browsers, mail providers, and share
destinations are third-party services. Their availability, terms, retention,
and account rules are outside Prio's control.

## 6. Backup, export, and restore

Android Google Drive backup is optional, requests only `drive.appdata`
(private app-data) access, never your account email or profile, and encrypts
backup content before upload to the app's private Drive area. Google still
receives OAuth authorization, network, file, and ciphertext metadata. Android
system Auto Backup is disabled.

iCloud backup controls are visible in Settings. Availability requires the app's
iCloud capability, an available iCloud account and container, network access,
and your explicit opt-in. When available and enabled, Prio encrypts backup
contents with AES-256-GCM before uploading them to app-specific iCloud storage;
the decryption key remains local. Prio marks its internal database and generated
local backup files excluded from Apple-managed device backup and protects them
for access after first unlock.

Manual exports are plaintext JSON. A share destination can read them. Backups
or restores can fail because of deletion, corruption, key loss, account state,
platform behavior, network failure, version incompatibility, or third-party
service changes. Verify important backups and protect exported files.

## 7. Acceptable use

You must not:

- use Prio to violate law, intellectual-property rights, privacy, or security;
- attempt to bypass access controls, extract another user's data, or interfere
  with Prio or a third-party service;
- use connected-agent, sharing, or AI features without authorization to expose
  another person's confidential information;
- distribute malware or abusive content through Prio-generated exports or
  integrations; or
- represent generated output as guaranteed accurate.

## 8. Privacy

The [Privacy Policy](/privacy-policy.html) explains local processing, Firebase
defaults, remote AI, sharing, credentials, backups, store checks, and other
network flows. Deleting local data does not automatically delete copies already
received by a third party.

## 9. Availability and changes

Prio is provided on an "as available" basis. Features may differ by platform,
OS version, device capability, region, provider availability, or store policy.
We may fix, change, suspend, or remove features for reliability, privacy,
security, legal, or product reasons.

We may update these Terms when shipped behavior or law changes. Material
changes will update the effective date and, where required, be presented in the
app.

## 10. Disclaimers and limitation of liability

To the maximum extent permitted by law, Prio is provided without warranties of
merchantability, fitness for a particular purpose, non-infringement, continuous
availability, or error-free AI output.

To the maximum extent permitted by law, Prio's developer is not liable for
indirect, incidental, special, consequential, or punitive damages, or for loss
of data, credentials, productivity, revenue, or opportunity arising from use of
Prio or a third-party service. Nothing in these Terms excludes liability that
cannot legally be excluded.

## 11. Termination

You may stop using Prio at any time. Delete local data, credentials, backups,
exports, and third-party copies using the controls described in the Privacy
Policy. Android and iOS expose **Delete All Data** for app-owned local data. Use
the in-app deletion controls before uninstalling if you want device-only
Keychain items removed; uninstall alone may not remove them.

We may restrict access where required by law or necessary to protect users,
services, or security.

## 12. Governing rules and platform terms

These Terms operate alongside mandatory consumer law and the applicable rules
of Google Play, the Apple App Store, and any third-party service you choose.
Platform-specific rules do not replace rights that cannot be waived under local
law.

## 13. Contact

Questions about these Terms may be sent to **mik.prio.ai@gmail.com**.

# Downloads of SmartLists App

`version.json` tells the app (the version installed from this website) which version is current.

To publish a version:

1. Put the APK here, e.g. `smartlists-go-0.2.0.apk` (or upload it as a GitHub release asset).
2. Fill in `version.json`:
   - `version`: the version of that APK, e.g. `0.2.0` (must match `version:` in the app's `pubspec.yaml`)
   - `apk`: the full `https://` address of the file, e.g. `https://ha-smartlists.com/downloads/smartlists-go-0.2.0.apk`
   - `sha256`: checksum of the file (optional, shown for comparison)
   - `released`: date, e.g. `2026-12-01`
   - `notes`: one or two sentences per language (`de`, `en`, …)
3. Push. Apps see the new version at their next check.

While `version` or `apk` is empty, the app reports no update.

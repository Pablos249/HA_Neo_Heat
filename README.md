# Neoheat Local

Experimental, community-maintained Home Assistant integration
for the local TCP stream observed with Neoheat EKO II and a USR-W600 converter.
Independent project, not affiliated with the manufacturer.

## Status

- Local protocol checked against one EKO II 15 installation, HMI firmware 218.
- Temperatures, compressor frequency, fan speeds, current and voltage.
- Read-only binary states for circulation pumps P0, P1 and P2.
- Optional diagnostic sensors for runtimes, settings, heating curves, versions
  and raw configuration states.
- UI configuration and reconfiguration, CRC checking, automatic reconnect.
- No cloud credentials. All entities are read-only.
- Local write control was removed after testing showed that an isolated command
  can halt local and cloud communication until the heat pump is restarted.
- Field mapping is empirical. Compatibility with other models is unverified.
- Protocol tests run without Home Assistant. A real HA installation test is
  still required before calling this release stable.

The converter must already expose the compatible stream on a TCP port.
An open port 502 alone does not mean this protocol is supported. This is not
standard Modbus TCP. The integration cannot create a missing local endpoint.
Do not reconfigure a working converter just to try this integration.

## Install with HACS

Using `https://github.com/Pablos249/HA_Neo_Heat`:

1. In HACS open **Custom repositories**, add that repository URL and select
   **Integration**.
2. Download **Neoheat Local (Experimental)** and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → Neoheat**.
4. Enter the local hostname/IP and TCP port (default 502). Validation may take
   30 seconds. The address is stored only in your Home Assistant configuration.

Requires Home Assistant 2025.1 or later (declared baseline, not a tested matrix).
To install manually, copy `custom_components/neoheat` into your HA
`config/custom_components` directory and restart. No Python scripts need to
run on another computer.

## Operation and limits

Expected telemetry interval is about 10 seconds. On failure sensors become
unavailable, then recover when a valid stream returns. Settings arrive less
often and remain unavailable until received; they are cleared on reconnect.
Uncertain mappings are disabled by default; enable them in the entity registry
only if useful for your own comparison. No `climate` or `switch` entities are
provided. No writable entities are provided. Units for raw pressure/opening values are not
assumed. Heating/Auto numeric codes are not decoded.

Pump P0, P1 and P2 states and compressor frequency are enabled by default.
Settings and less certain fields are diagnostic entities disabled by default;
enable selected entities from the Neoheat device page when needed.

Change the endpoint through the integration's **Reconfigure** menu. Remove the
integration in Devices & services to stop its connection. Only one reader per
endpoint is recommended until the converter's client limit is known.

## Publishing / privacy

See [PUBLISHING.md](PUBLISHING.md). The public package uses an explicit file
allowlist; local captures, screenshots and research notes are excluded.
No serial number, MAC, household IP, cloud login or personal author name is
required in the source. GitHub account names and Git commit author metadata
are public separately from file contents: use a project alias and GitHub's
private `noreply` email if you want to avoid exposing personal details.

Please do not attach raw captures or screenshots containing identifiers to
public issues. Describe model, firmware, symptoms and sanitized values.

## Development

```sh
python -m unittest discover -s tests -v
```

Tests use generated packets with invented headers, never real device captures.
See [PROTOCOL.md](PROTOCOL.md) for the observed frame format and limitations.

## Instalacja po polsku

W HACS dodaj adres opublikowanego repozytorium jako **Integracja**, pobierz
Neoheat Local i zrestartuj HA. Następnie dodaj Neoheat przez **Ustawienia →
Urządzenia i usługi** i wpisz lokalny adres konwertera oraz port. Pierwsza
wersja jest eksperymentalna i obsługuje wyłącznie odczyt. Hasło do chmury nie
jest potrzebne. Repozytorium:
`https://github.com/Pablos249/HA_Neo_Heat`.

License: MIT.

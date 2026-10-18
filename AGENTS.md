# AGENTS.md — battage

Battery history summariser for Linux laptops. Reads upower's charge log and prints
three lines: current charge, how long ago the battery was last at/near full, and how
the current charge cycle split between **awake** and **asleep** time (hours, percent
burned, average watts). Personal tool for one ThinkPad; it is a single Python script
with no third-party dependencies.

## Layout

| path | what |
|---|---|
| `battage` | the entire program — one executable Python 3 script, stdlib only |
| `install.sh` | Fedora installer: checks Python 3 + upower, installs to `~/.local/bin/battage`; `./install.sh uninstall` removes it |
| `README.md` | user-facing docs — update it in the same commit as a behaviour change |

## Invariants — do not break these

- **Standard library only.** `battage` has to stay one file that can be copied to any
  Linux box. A pip dependency is a design change, not an implementation detail.
- **The sleep/awake split.** A gap between adjacent samples is sleep only when it is
  longer than `--gap` (default 15 min) **and** the battery drained slower than
  `SLEEP_RATE_MAX` (5 %/h) across it. Both conditions matter: a busy machine crossing
  a logging gap burns 10–15 %/h and must stay awake time. Loosening either one turns
  real work into fake sleep.
- **Drop `state=unknown` / `0 %` rows first** (`VALID_STATES` in `read_rows`). upower
  writes them around resumes and reboots; they would fake a huge drop across a gap.
- **Wattage uses `energy_full`, never `energy_design`** — upower's percentage is
  relative to the *current* full capacity. Batteries reporting charge instead of energy
  go through `charge_full * voltage_now`. If neither is readable, print no wattage:
  never guess one.
- **Output shape is a contract.** Three lines, in order, `used:` / `sleep:` prefixed —
  humans and scripts both parse it by eye. Adding fields is fine; reordering is not.
- `last full charge` = the latest sample at or above the threshold **while
  discharging**. The current cycle is everything from there on (`hits[-1]` in `main`).

## Testing without a battery

`-f/--file` accepts any upower history file, so a synthetic fixture covers everything.
Format is tab-separated `unixtime<tab>percent<tab>state`, states limited to
`charging`, `discharging`, `fully-charged`, `pending-charge`.

```bash
cd ~/Documents/Git/battage
now=$(date +%s)
printf '%s\t%s\t%s\n' \
  "$((now-57600))" 97 discharging \
  "$((now-55800))" 92 discharging \
  "$((now-54000))" 88 discharging \
  "$((now-14400))" 86 discharging \
  "$((now-12600))" 80 discharging \
  "$((now-10800))" 74 discharging > /tmp/hist.dat
./battage -f /tmp/hist.dat
# expect: used  2.0 hours, burned 21% / sleep 11.0 hours, burned 2%
```

The 11-hour jump is the sleep gap (large, low drain); the rest is awake time. Use `-t`
and `-g` to pin the threshold and gap when asserting on numbers. Note that the first
line (`Your current charge is …%`) and the wattages come from live
`/sys/class/power_supply` — on a machine without those they are absent or omitted, which
is expected behaviour, not a regression. `README.md` documents the exact maths.

## Conventions

- Commits: `battage: <imperative summary>`, e.g. `battage: split sleep from awake time`.
- MIT, author monochrome. Keep comments explaining *why* a threshold or fallback exists —
  several of them are the result of a real misdiagnosis.

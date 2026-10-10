# battage

Battery history summariser for Linux laptops, driven by [upower](https://upower.freedesktop.org/)'s
charge log. It answers two questions from `/var/lib/upower/history-charge-*.dat`:

- how long ago the battery was last charged to (near) full;
- how much of the current charge cycle the machine spent **asleep vs in use**, and how much
  battery was burned while asleep.

## Output

```
$ battage
Your current charge is 39%
last full charge was 11.5 hours ago  (Sat 10 Oct 04:31)
used:  3.2 hours
sleep: 8.2 hours, burned 8% battery
```

- **`last full charge`** — the first sample at/above the threshold (default 97%) while discharging.
- **`used`** — awake time in the current charge cycle.
- **`sleep`** — time the machine was asleep/off, and the net percent lost across those periods.

The `used` + `sleep` hours sum to the age of the current charge cycle.

## How the sleep/awake split works

upower stops sampling while the machine is suspended, so a gap between adjacent samples much larger
than its normal polling cadence (~3 min) is a period where the machine was away. But a big gap alone
isn't enough — a busy machine can also cross a logging gap while burning 14 %/h — so a gap only
counts as sleep when **both** hold:

1. it is longer than the `--gap` cutoff (default 15 min), and
2. the battery drained slower than 5 %/h across it (real sleep here runs 0.5–3 %/h).

Everything else is counted as awake time. Battery burned asleep is the net percent lost across the
sleep gaps (counted when the period starts discharging, even if it ends on the charger). upower's
`state=unknown` / `0%` rows, which it writes around resumes and reboots, are dropped first — they
would otherwise fake a huge drop.

**Caveat:** a suspend and a power-off look identical in this log (upower samples neither), so
"sleep" strictly means "the machine wasn't running".

## Requirements

- Linux with **upower** running (it produces the history file).
- **Python 3** — the script is pure standard library, no third-party packages.

Fedora users: `./install.sh` checks both and installs whatever is missing with `dnf`.

## Install (Fedora)

```bash
git clone https://github.com/get-monochromed/battage.git
cd battage
./install.sh
```

Installs `battage` to `~/.local/bin/battage` (no root needed for that part; `sudo` is used only if a
dependency has to be installed). It will tell you if `~/.local/bin` isn't on your `PATH`.

### Upgrade

`install.sh` overwrites in place, so just pull and re-run:

```bash
cd battage
git pull
./install.sh
```

### Uninstall

```bash
cd battage
./install.sh uninstall
```

or simply `rm ~/.local/bin/battage`.

## Manual install (any distro)

```bash
install -m755 battage ~/.local/bin/battage
```

## Usage

```
battage [-f FILE] [-t LEVEL] [-g MINUTES]

  -f, --file       upower charge history file (default: newest in /var/lib/upower)
  -t, --threshold  charge level to count as full (default 97)
  -g, --gap        minutes between samples above which the machine may have been
                   asleep (default 15)
```

## License

MIT

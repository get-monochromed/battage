# battage

A standard-library Python command for summarizing Linux battery charge history recorded by upower.

```text
$ battage
Your current charge is 39%
last qualifying discharge began 11.5 hours ago  (Sat 10 Oct 04:31)
used:  3.2 hours, burned 28% battery, 3.9 W average (estimated)
sleep: 8.2 hours, burned 8% battery, 0.4 W average (estimated)
history ends: Sat 10 Oct 15:55; excluded charging/ambiguous intervals: 0.0 hours
```

The start is the first discharging sample of the most recent continuous discharging run containing a sample at or above the threshold (94% by default). If there is no qualifying run, the available history is summarized instead. A partial recharge ends a run; charging and later discharge intervals can appear in the summary after the selected start.

The `used` and `sleep` figures are estimates over recorded intervals only. A discharging interval is classified as sleep when it is longer than `--gap` (15 minutes by default) and its drain is at most 5% per hour; other discharging intervals are counted as used. Long gaps may also represent shutdown, idle time, or interrupted logging, and rapid sleep drain can look like use. A discharge interval ending on AC is attributed to discharge. Intervals starting on AC and intervals with rising charge are excluded and reported separately. The final history sample can be older than the current time, so the interval totals need not equal the elapsed time since the start.

Average watts are estimated from percentage lost, the battery's current full-charge energy, and interval duration. Small changes and short intervals are noisy. If full energy is unavailable, wattage is omitted; for charge-based batteries, full charge and current voltage provide an approximation. Unknown-state and invalid samples are discarded.

Live charge and wattage are shown only when the automatically selected history has an unambiguous association: a unique model and serial match, or exactly one system battery and one non-peripheral history file. An explicit `--file` never borrows live battery data. The newest non-peripheral history is selected by default, falling back to other histories if none exists; check `--file` when multiple devices are present.

## Usage

```text
battage [-f FILE] [-t LEVEL] [-g MINUTES]
  -f, --file       upower charge history file
  -t, --threshold  near-full charge percentage, 0–100 (default 94)
  -g, --gap        possible sleep gap in minutes, greater than zero (default 15)
```

Linux, Python 3 and an upower charge history are required. Run the tests with `python3 -m unittest discover -s tests -v`.

## Installation

On Fedora, `./install.sh` installs a copy to `~/.local/bin/battage`; rerun it after updates. `./install.sh uninstall` removes the installed command. For a live link to a checkout instead, use:

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/battage" ~/.local/bin/battage
```

Run this from the checkout, after moving or removing any existing destination. Changes to the checked-out script then take effect immediately.

## License

MIT

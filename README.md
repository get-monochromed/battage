# battage

A standard-library Python command for summarizing Linux battery charge history recorded by upower.

```text
$ battage
Charge: 39%
Discharge: 80% (partial), 11.5 h ago (Sat 10 Oct 04:31)
used:  3.2 h, 28% drained, 3.9 W avg (est.)
sleep: 8.2 h, 8% drained, 0.4 W avg (est.)
History through Sat 10 Oct 15:55
```

The latest discharge starts with the first discharging sample after a recorded external-power state, regardless of whether it starts at 80%, 100%, or another level. Time spent plugged in at full charge is excluded. The `Discharge` line gives the first observed discharging sample, not necessarily the exact unplugging time. Short notices appear when the start is unknown, a charge was missed, or the discharge has ended. Excluded charging/uncertain time is shown only when nonzero. `est.` marks estimated figures.

If charging was missed by the logger (for example, during suspend), a rise of at least 2 percentage points between discharging samples indicates an unrecorded charge and starts a new cycle at the later sample. A one-point rise may be gauge noise and does not restart the cycle. Very small unrecorded charges may therefore be missed; other gauge jumps may be mistaken for a charge. If the latest history is charging, the preceding discharge is reported as ended. A live charging status can reveal a transition newer than the history, but does not provide its time.

The `used` and `sleep` figures are estimates over recorded intervals only. A discharging interval is classified as sleep when it is longer than `--gap` (15 minutes by default) and its drain is at most 5% per hour; other discharging intervals are counted as used. Long gaps may also represent shutdown, idle time, or interrupted logging, and rapid sleep drain can look like use. A discharge interval ending on AC is attributed to discharge. Intervals starting on AC and intervals with rising charge are excluded and reported separately. The final history sample can be older than the current time, so the interval totals need not equal the elapsed time since the start.

Average watts are estimated from percentage lost, the battery's current full-charge energy, and interval duration. Small changes and short intervals are noisy. If full energy is unavailable, wattage is omitted; for charge-based batteries, full charge and current voltage provide an approximation. Unknown-state and invalid samples are discarded.

Live charge and wattage are shown only when the automatically selected history has an unambiguous association: a unique model and serial match, or exactly one system battery and one non-peripheral history file. An explicit `--file` never borrows live battery data. The newest non-peripheral history is selected by default, falling back to other histories if none exists; check `--file` when multiple devices are present.

## Usage

```text
battage [-f FILE] [-t LEVEL] [-g MINUTES]
  -f, --file       upower charge history file
  -t, --threshold  near-full label threshold, 0–100 (default 94); does not select the cycle
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

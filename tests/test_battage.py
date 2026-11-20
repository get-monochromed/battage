import importlib.machinery
import importlib.util
import os
import subprocess
import tempfile
import unittest

PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'battage')
loader = importlib.machinery.SourceFileLoader('battage', PATH)
spec = importlib.util.spec_from_loader(loader.name, loader)
battage = importlib.util.module_from_spec(spec)
loader.exec_module(battage)


class BatteryHistoryTests(unittest.TestCase):
    def test_partial_charge_and_full_plateau_start_at_unplug(self):
        for percent in (80, 97, 100):
            with self.subTest(percent=percent):
                rows = [(0, 30, 'charging'), (3600, percent, 'charging'),
                        (10800, percent, 'fully-charged'),
                        (10801, percent, 'discharging'), (12000, percent - 2, 'discharging')]
                self.assertEqual(battage.find_cycle(rows), (3, None, 'power-state transition'))

    def test_unrecorded_charge_and_gauge_noise(self):
        rows = [(0, 94, 'discharging'), (1, 14, 'discharging'),
                (100, 100, 'discharging'), (101, 99, 'discharging'),
                (102, 100, 'discharging'), (103, 98, 'discharging')]
        self.assertEqual(battage.find_cycle(rows), (2, None, 'unrecorded charge'))

    def test_cycle_when_currently_charging_or_no_discharge(self):
        rows = [(0, 80, 'discharging'), (1, 70, 'discharging'),
                (2, 70, 'charging'), (3, 90, 'charging')]
        self.assertEqual(battage.find_cycle(rows), (0, 3, 'first sample'))
        self.assertEqual(battage.find_cycle(rows[2:]), (None, None, None))

    def test_latest_partial_run_not_old_full_run(self):
        rows = [(0, 100, 'discharging'), (1, 40, 'discharging'),
                (2, 80, 'charging'), (3, 80, 'discharging'), (4, 70, 'discharging')]
        self.assertEqual(battage.find_cycle(rows), (3, None, 'power-state transition'))

    def test_activity_excludes_charging_and_rises(self):
        rows = [(0, 99, 'discharging'), (1800, 94, 'discharging'),
                (41400, 92, 'discharging'), (43200, 85, 'charging'),
                (45000, 90, 'discharging'), (46800, 91, 'discharging')]
        sleep, sleep_burn, used, used_burn, other = battage.analyze_activity(rows, 900)
        self.assertEqual((sleep, sleep_burn, used, used_burn, other), (11, 2, 1, 12, 1))

    def test_bad_rows_filtered_and_duplicate_timestamps_ignored(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('1\t99\tdischarging\n1\t98\tdischarging\n2\tnan\tdischarging\n'
                    '3\t101\tdischarging\n4\t0\tunknown\n5\t97\tdischarging\n')
            path = f.name
        try:
            rows = battage.read_rows(path)
            self.assertEqual(len(rows), 3)
            self.assertEqual(battage.analyze_activity(rows, 900)[3], 1)
        finally:
            os.unlink(path)

    def test_cli_validation_and_missing_file(self):
        for args in (['-g', 'nan'], ['-t', '101'], ['-f', '/no/such/battage/history']):
            result = subprocess.run([PATH, *args], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('Traceback', result.stderr)

    def test_explicit_history_does_not_mix_live_battery(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write('1\t99\tdischarging\n3601\t89\tdischarging\n')
            f.flush()
            result = subprocess.run([PATH, '-f', f.name], text=True, capture_output=True, check=True)
        self.assertIn('used:  1.0 h, 10% drained', result.stdout)
        self.assertNotIn('Charge:', result.stdout)
        self.assertNotIn(' W avg', result.stdout)


if __name__ == '__main__':
    unittest.main()

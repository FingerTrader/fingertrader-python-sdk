# Python projects with native FQE backtesting

The experimental hosted interface uses `finger_trader.hosted.Strategy`. The
Desktop host freezes all project files, parameters and SDK assets before it
starts a worker. Helpers can be imported from the project directory. The SDK
never receives broker credentials and does not implement a second ledger.

Declare indicator instances during `on_start`, then read them during each
`on_bar`. Parameters use FQE catalog names and decimal/integer strings. Defaults
are the catalog's versioned defaults; explicit parameters are recommended.
`None` means not yet valid, including warmup. Instance IDs and parameters cannot
change after the first bar. Different IDs have independent native state.

```python
from decimal import Decimal
from finger_trader.hosted import Strategy


class UserStrategy(Strategy):
    def on_start(self, ctx):
        self.macd_parameters = {
            "fast": "12",
            "slow": "26",
            "signal": "9",
            "source": "close",
            "oscillator_ma_type": "ema",
            "signal_ma_type": "ema",
            "histogram_multiplier": "1.0",
        }
        ctx.indicator("trend", "macd", parameters=self.macd_parameters)
        self.previous = None
        self.sequence = 0

    def on_bar(self, bar):
        self.sequence += 1
        ctx = self.context
        values = ctx.indicator("trend", "macd", parameters=self.macd_parameters)
        line, signal = values.get("macd_line"), values.get("signal_line")
        if line is None or signal is None:
            return
        difference = line - signal
        previous, self.previous = self.previous, difference
        if previous is None or ctx.is_warmup:
            return
        held = ctx.position().quantity
        if previous <= 0 < difference and held == 0:
            ctx.submit_order(
                client_order_id=f"entry.{self.sequence}", side="buy", quantity=Decimal("1")
            )
        elif previous >= 0 > difference and held > 0:
            ctx.submit_order(client_order_id=f"exit.{self.sequence}", side="sell", quantity=held)
```

`indicators.read` is a separately granted capability. Only the active callback's
owner thread can call it. Numeric outputs are immutable `Decimal` values. The
SDK does not round, scale, seed or locally recompute native indicators.

FQE owns matching, fees, cash/margin admission and protective orders. A request
is not a fill: query its order status and subsequent account/position snapshots.
Research orders fill under the same native execution policies as visual graph
orders. Explicit requested quantity is an upper bound even with margin sizing.
Start, warmup and stop callbacks cannot submit orders. Pending orders are
cancelled on terminal completion. Stopping and starting creates a new session;
it does not resume a prior cursor or replay a previous report.

The hosted protocol remains `mode="backtest"`. Real-account Python routing and
independent SDK package installation are not implemented by this interface.
Installing this source checkout does not confer live order authority or replace
the SDK/engine versions shipped inside a signed Desktop application. Do not use
this experimental backtest interface as evidence of live-trading readiness.

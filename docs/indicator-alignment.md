# Chart and native indicator alignment

The existing Python `SMA`, `sma`, `crosses_above`, and `crosses_below` helpers are
standalone utilities. They do not submit orders or replace the native rule engine.
SMA uses binary64, adds the new observation before subtracting the expired one,
and returns `None` until a complete window exists. Crossover predicates require
four finite observations; equality is on the previous side of a crossing.
These semantics agree with Desk's chart-compatible SMA and native crossings.
The chart's early MA zero is a drawing sentinel, not a ready trading value.

Desk/native research sessions explicitly select `finger.k-chart/1`. It is distinct
from the unchanged exact-decimal reference-provider profile. That chart profile
uses first-price EMA seeds, zero-seeded RSI gain/absolute-difference smoothing,
MACD histogram `2*(DIF-DEA)`, and BOLL sample deviation (`n-1`). Unready and
undefined outputs remain null. Do not reconstruct a different RSI/MACD in a Python
adapter and present it as a native strategy observation. Those helpers are not
currently part of this Python SDK's public indicator API.

Transport is part of the contract. Desk's realtime line uses its existing ask
price, one replaceable point per UTC 500ms bucket, and a rolling 120-second
window. In Desk's chart-compatible quote adapter the `close` display series is
that ask series; explicitly selected ask/bid/mid inputs retain their meanings.
Raw HTTP/WebSocket responses in this SDK remain unchanged. A Python caller must
choose the same price field, periods, ordered prefix, bucket replacement and
window policy before comparing computed values. A raw tick is not a new bar.
Closed-bar evaluation uses confirmed bars and preserves its initialization
prefix; an unfinished candle is not a confirmed order signal.

Native responses carry `chart_columns` and `chart_sample` from the evaluation
that emitted intents; single-source warmup also returns `chart_samples`. Use
those observations with resolved node settings for rendering. Keep node/source
identities and null readiness; do not mix periods, products, chart animation
anchors, or account fills with indicator observations.

This documents interoperability only; it adds no Python SDK native-engine
client or new trading mutation methods. No API envelopes or dependencies change.

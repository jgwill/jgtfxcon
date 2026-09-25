"""What jgwill/jgtsrc consumes from jgtfxcon. A change that fails here breaks jgtsrc.

Consumers, 2026-09-25:
- jgt-data-server/updater/src/fetch_worker.py holds a ForexConnect session per
  worker and asserts this shape in pin_check(); it falls back to spawning
  jgtfxcli when the shape changes.
- jgt-transact/src/providers/fxcm_bridge.py shells out to the order commands.

Run against the installed package: pytest tests/test_jgtsrc_contract.py
"""
import importlib.metadata as md

import pandas as pd


def _fetch_worker_modules():
    from jgtfxcon import jgtfxcli  # adds the package folder to sys.path, as fetch_worker relies on
    import JGTPDS
    import JGTPDSSvc
    import jgtfxc
    return jgtfxcli, JGTPDS, JGTPDSSvc, jgtfxc


def test_the_held_session_surface_exists():
    jgtfxcli, pds, svc, jfx = _fetch_worker_modules()
    assert "fx" in vars(jfx), "fetch_worker clears jgtfxc.fx to force a login"
    assert "fx" in jfx.connect.__code__.co_names, "connect() must read the fx global"
    assert "connection_status" in vars(jfx.jgtfxcommon)
    assert callable(jfx.jgtfxcommon.get_connection_status)
    for name in ("stayConnectedSetter", "disconnect"):
        assert callable(getattr(pds, name))
    for name in ("getPH", "getPHs"):
        assert callable(getattr(svc, name))
    assert callable(jgtfxcli._parse_args)


def test_the_commands_jgtsrc_and_jgtml_call_are_installed():
    ours = {e.name for e in md.entry_points(group="console_scripts") if e.value.startswith("jgtfxcon.")}
    transact = {"fxaddorder", "fxrmorder", "fxtr", "fxopen", "fxclose"}
    updater = {"jgtfxcli"}
    jgtapp = {"fxmvstop", "fxrmtrade", "pdscli"}
    assert transact | updater | jgtapp <= ours


def _frame(rows):
    cols = ["Date", "BidOpen", "BidHigh", "BidLow", "BidClose", "AskOpen", "AskHigh", "AskLow", "AskClose", "Volume"]
    return pd.DataFrame(rows, columns=cols)


def _real(d, p):
    return [d, p, p + .001, p - .001, p, p + .0001, p + .0011, p - .0009, p + .0001, 100]


def _placeholder(d):
    return [d] + [1.0] * 8 + [55]


def test_placeholder_candles_are_refused_with_the_history_merge_rule():
    _, pds, _, _ = _fetch_worker_modules()
    refuse = pds._refuse_placeholder_candles
    head = refuse(_frame([_placeholder("t0"), _real("t1", 1.1), _real("t2", 1.1), _real("t3", 1.1)]))
    assert list(head.Date) == ["t1", "t2", "t3"]
    edge = refuse(_frame([_real("t0", 1.1), _real("t1", 1.1), _placeholder("t2"), _real("t3", 1.1)]))
    assert list(edge.Date) == ["t0", "t1"], "a placeholder in the last two rows cuts the frame there"
    near = refuse(_frame([_real("t0", 0.99), ["t1", 1.0, 1.0, 1.0, 1.0, 1.0002, 1.0002, 1.0002, 1.0002, 9]]))
    assert list(near.Date) == ["t0", "t1"], "a real quote near 1.0 is kept"

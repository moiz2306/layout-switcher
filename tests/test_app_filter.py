from app_filter import AppFilter
from config import Config


def test_no_exclusions():
    cfg = Config(path="/nonexistent")
    af = AppFilter(cfg)
    assert af.is_excluded("Terminal") is False
    assert af.is_excluded("Safari") is False


def test_with_exclusions():
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("excluded_apps:\n  - Terminal\n  - iTerm2\n")
        f.flush()
        cfg = Config(path=f.name)
    os.unlink(f.name)
    af = AppFilter(cfg)
    assert af.is_excluded("Terminal") is True
    assert af.is_excluded("iTerm2") is True
    assert af.is_excluded("Safari") is False


def test_case_insensitive():
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("excluded_apps:\n  - terminal\n")
        f.flush()
        cfg = Config(path=f.name)
    os.unlink(f.name)
    af = AppFilter(cfg)
    assert af.is_excluded("Terminal") is True
    assert af.is_excluded("TERMINAL") is True


def test_get_active_app_returns_string():
    af = AppFilter(Config(path="/nonexistent"))
    app_name = af.get_active_app()
    assert isinstance(app_name, str)
    assert len(app_name) > 0

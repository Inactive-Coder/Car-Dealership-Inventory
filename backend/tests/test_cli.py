from app import cli
from app.services.auth import AdminAlreadyProvisionedError


class SessionContext:
    def __init__(self):
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True


def test_create_admin_prompts_without_echoing_password(monkeypatch, capsys):
    session = SessionContext()
    provided = {}
    answers = iter(["operator@example.com"])
    passwords = iter(["a-strong-admin-password", "a-strong-admin-password"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    monkeypatch.setattr(cli.getpass, "getpass", lambda _prompt: next(passwords))
    monkeypatch.setattr(cli, "SessionLocal", lambda: session)

    def provision(payload, active_session):
        provided["payload"] = payload
        provided["session"] = active_session

    monkeypatch.setattr(cli, "provision_initial_admin", provision)

    assert cli.create_admin() == 0
    output = capsys.readouterr().out
    assert "Administrator account created" in output
    assert "a-strong-admin-password" not in output
    assert provided["payload"].email == "operator@example.com"
    assert session.closed


def test_create_admin_stops_when_password_confirmation_differs(monkeypatch):
    passwords = iter(["a-strong-admin-password", "a-different-password"])
    monkeypatch.setattr("builtins.input", lambda _prompt: "operator@example.com")
    monkeypatch.setattr(cli.getpass, "getpass", lambda _prompt: next(passwords))
    monkeypatch.setattr(cli, "SessionLocal", lambda: (_ for _ in ()).throw(AssertionError("database must not open")))

    assert cli.create_admin() == 2


def test_create_admin_reports_repeat_bootstrap_without_changes(monkeypatch, capsys):
    session = SessionContext()
    passwords = iter(["a-strong-admin-password", "a-strong-admin-password"])
    monkeypatch.setattr("builtins.input", lambda _prompt: "operator@example.com")
    monkeypatch.setattr(cli.getpass, "getpass", lambda _prompt: next(passwords))
    monkeypatch.setattr(cli, "SessionLocal", lambda: session)
    monkeypatch.setattr(cli, "provision_initial_admin", lambda *_: (_ for _ in ()).throw(AdminAlreadyProvisionedError()))

    assert cli.create_admin() == 1
    assert "already provisioned" in capsys.readouterr().err
    assert session.closed

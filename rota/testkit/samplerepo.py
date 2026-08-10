"""
The sample repository — a codebase the system can be pointed at.

Invented rather than found. Stage 7 asserts on properties that must be
*discovered*, and a real repository has none of them planted; cloning one needs
network and pinning; vendoring one puts somebody else's licence in this tree.

It has to look like a repository somebody wrote. That means short comments where
a real developer would write one and none anywhere else, a little inconsistency
between modules written at different times, no scaffolding narration, and no
file that exists only to demonstrate something. If it reads as a fixture, the
roles are being tested against a strawman.

Two languages, because the indexer must be language-agnostic and a single-
language sample would let a Python-only shortcut pass.

**The planted properties** — what stage 7 must find, recorded here so the
assertions and the fixture cannot drift apart:

  collision   `account` means the login identity in `auth/` and the billing
              entity in `billing/`. Both modules use the bare word.
  fan_in      `store/` is imported by every other module and owns the persisted
              schema — the shape of a real external commitment.
  barren      `notify/` is templates and formatting. Nothing in it outlives a
              process or crosses a boundary, so a survey should find nothing
              and constraint zero should shrink by exactly that area.
  bound_diff  a change to `store/` touches a grain a constraint would bind.
  free_diff   a change to `notify/` touches nothing bound.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

PLANTED = {
    "collision": {
        "term": "account",
        "senses": {
            "src/auth/accounts.py": "the login identity",
            "src/billing/accounts.py": "the billing entity that owes money",
        },
    },
    "fan_in": {"module": "src/store", "imported_by":
               ["src/auth", "src/billing", "src/catalog", "src/notify"]},
    "barren": {"module": "src/notify"},
    "bound_diff": {"path": "src/store/records.py"},
    "free_diff": {"path": "src/notify/templates.py"},
}

FILES: dict[str, str] = {}


def _add(path: str, body: str) -> None:
    FILES[path] = body.lstrip("\n")


# ---------------------------------------------------------------------------
# store — the persisted layer. High fan-in, owns the schema.
# ---------------------------------------------------------------------------

_add("src/store/__init__.py", """
from .connection import connect, transaction
from .records import Record, load, save

__all__ = ["connect", "transaction", "Record", "load", "save"]
""")

_add("src/store/connection.py", """
import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("BILLING_DSN", "billing.db")


def connect(dsn=None):
    conn = sqlite3.connect(dsn or _DSN)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
""")

_add("src/store/records.py", """
from dataclasses import dataclass, field

from .connection import connect, transaction


@dataclass
class Record:
    table: str
    id: str
    values: dict = field(default_factory=dict)


def load(table, id, conn=None):
    conn = conn or connect()
    row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (id,)).fetchone()
    return Record(table, id, dict(row)) if row else None


def save(record, conn=None):
    conn = conn or connect()
    cols = list(record.values)
    marks = ", ".join("?" for _ in cols)
    with transaction(conn):
        conn.execute(
            f"INSERT OR REPLACE INTO {record.table} (id, {', '.join(cols)}) "
            f"VALUES (?, {marks})",
            [record.id, *record.values.values()],
        )
    return record.id


def delete(table, id, conn=None):
    conn = conn or connect()
    with transaction(conn):
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
""")

_add("src/store/schema.sql", """
CREATE TABLE IF NOT EXISTS accounts (
    id          TEXT PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    status      TEXT NOT NULL DEFAULT 'active',
    created_seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS invoices (
    id         TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(id),
    total_cents INTEGER NOT NULL,
    state      TEXT NOT NULL DEFAULT 'draft'
);

CREATE TABLE IF NOT EXISTS charges (
    id         TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES invoices(id),
    amount_cents INTEGER NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(id),
    expires_seq INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    sku        TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    price_cents INTEGER NOT NULL
);
""")

_add("src/store/migrations.py", """
from .connection import connect, transaction

MIGRATIONS = [
    ("0001_initial", "src/store/schema.sql"),
    ("0002_invoice_state", "ALTER TABLE invoices ADD COLUMN voided_reason TEXT"),
]


def applied(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY)")
    return {r["name"] for r in conn.execute("SELECT name FROM _migrations")}


def run(conn=None):
    conn = conn or connect()
    done = applied(conn)
    for name, source in MIGRATIONS:
        if name in done:
            continue
        sql = open(source).read() if source.endswith(".sql") else source
        with transaction(conn):
            conn.executescript(sql)
            conn.execute("INSERT INTO _migrations (name) VALUES (?)", (name,))
""")


# ---------------------------------------------------------------------------
# auth — where `account` means the login identity
# ---------------------------------------------------------------------------

_add("src/auth/__init__.py", """
from .accounts import Account, find_by_email, register
from .sessions import issue, revoke, verify
""")

_add("src/auth/accounts.py", r"""
import hashlib
import re
from dataclasses import dataclass

from ..store import Record, load, save

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Account:
    \"\"\"A person who can sign in. Not the thing an invoice is addressed to.\"\"\"
    id: str
    email: str
    status: str = "active"


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()


def register(id, email, password, seq):
    if not EMAIL.match(email):
        raise ValueError(f"not an email address: {email}")
    save(Record("accounts", id, {
        "email": email, "status": "active", "created_seq": seq}))
    save(Record("credentials", id, {"digest": _hash(password, id)}))
    return Account(id, email)


def find_by_email(email, conn=None):
    conn = conn or None
    rec = load("accounts", email, conn)
    return Account(rec.id, rec.values["email"], rec.values["status"]) if rec else None


def deactivate(id):
    rec = load("accounts", id)
    if rec is None:
        return False
    rec.values["status"] = "disabled"
    save(rec)
    return True
""")

_add("src/auth/sessions.py", """
import secrets

from ..store import Record, load, save

TTL = 60 * 60 * 12


def issue(account_id, seq):
    token = secrets.token_urlsafe(24)
    save(Record("sessions", token, {
        "account_id": account_id, "expires_seq": seq + TTL}))
    return token


def verify(token, seq):
    rec = load("sessions", token)
    if rec is None or rec.values["expires_seq"] < seq:
        return None
    return rec.values["account_id"]


def revoke(token):
    from ..store.records import delete
    delete("sessions", token)
""")

_add("src/auth/passwords.py", """
import hashlib
import secrets

from .accounts import _hash

RESET_TTL = 60 * 30


def make_reset_token():
    return secrets.token_urlsafe(18)


def check(password, digest, salt):
    return secrets.compare_digest(_hash(password, salt), digest)


def strength(password):
    if len(password) < 10:
        return "short"
    if password.isalpha() or password.isdigit():
        return "narrow"
    return "ok"
""")

_add("src/auth/README.md", """
# auth

Sign-in and sessions. An `account` here is a **login identity** — one person,
one email, one password. It is not the billing account; see `billing/`.
""")


# ---------------------------------------------------------------------------
# billing — where `account` means the thing that owes money
# ---------------------------------------------------------------------------

_add("src/billing/__init__.py", """
from .accounts import BillingAccount, balance, open_account
from .invoices import Invoice, issue_invoice, void
""")

_add("src/billing/accounts.py", """
from dataclasses import dataclass

from ..store import Record, load, save


@dataclass
class BillingAccount:
    \"\"\"Who the invoice is addressed to. May cover several login identities.\"\"\"
    id: str
    name: str
    terms_days: int = 30


def open_account(id, name, terms_days=30):
    save(Record("billing_accounts", id, {"name": name, "terms_days": terms_days}))
    return BillingAccount(id, name, terms_days)


def balance(account_id, conn=None):
    conn = conn or None
    rows = load("invoices", account_id, conn)
    if rows is None:
        return 0
    return sum(int(v) for k, v in rows.values.items() if k == "total_cents")


def close_account(account_id):
    # Closing does not delete: the invoices have to survive for seven years.
    rec = load("billing_accounts", account_id)
    if rec is None:
        return False
    rec.values["closed"] = 1
    save(rec)
    return True
""")

_add("src/billing/invoices.py", """
from dataclasses import dataclass, field

from ..store import Record, load, save
from .charges import Charge, total_of


@dataclass
class Invoice:
    id: str
    account_id: str
    state: str = "draft"
    charges: list = field(default_factory=list)


def issue_invoice(id, account_id, charges):
    total = total_of(charges)
    save(Record("invoices", id, {
        "account_id": account_id, "total_cents": total, "state": "issued"}))
    for charge in charges:
        save(Record("charges", charge.id, {
            "invoice_id": id, "amount_cents": charge.amount_cents,
            "description": charge.description}))
    return Invoice(id, account_id, "issued", charges)


def void(id, reason):
    rec = load("invoices", id)
    if rec is None or rec.values["state"] == "paid":
        return False
    rec.values["state"] = "void"
    rec.values["voided_reason"] = reason
    save(rec)
    return True
""")

_add("src/billing/charges.py", """
from dataclasses import dataclass


@dataclass
class Charge:
    id: str
    amount_cents: int
    description: str


def total_of(charges):
    return sum(c.amount_cents for c in charges)


def prorate(amount_cents, days_used, days_in_period):
    if days_in_period <= 0:
        raise ValueError("period must be positive")
    return round(amount_cents * days_used / days_in_period)
""")

_add("src/billing/subscriptions.py", """
from ..catalog.pricing import price_for
from .charges import Charge, prorate


def renew(account_id, sku, seq, period_days=30):
    price = price_for(sku)
    return Charge(f"ch_{account_id}_{seq}", price, f"{sku} renewal")


def upgrade(account_id, from_sku, to_sku, days_used, seq, period_days=30):
    credit = prorate(price_for(from_sku), period_days - days_used, period_days)
    charge = prorate(price_for(to_sku), period_days - days_used, period_days)
    return Charge(f"ch_{account_id}_{seq}", charge - credit, f"{from_sku} -> {to_sku}")
""")

_add("src/billing/README.md", """
# billing

Invoices, charges, subscriptions. An `account` here is the **billing entity** —
what an invoice is addressed to. One billing account may cover several login
identities, and closing one never deletes its invoices.
""")

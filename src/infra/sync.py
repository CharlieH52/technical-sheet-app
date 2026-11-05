"""Sincronización con la API de inventario (local-first).

Incluye el cliente HTTP (``urllib.request``), el constructor del payload y el
orquestador que envía las fichas pendientes una a una. Nunca bloquea la
persistencia local.
"""

from __future__ import annotations

import hashlib
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

AGENT_VERSION = "1.0.0"
SCHEMA_VERSION = 1


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_bool(name: str, default: bool = False) -> bool:
    value = _env(name, "true" if default else "false").lower()
    return value in {"1", "true", "yes", "on", "si", "sí"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(_env(name, str(default)))
    except ValueError:
        return default


def _truncate(value: Any, limit: int) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text[:limit] if len(text) > limit else text


def build_payload(computer: Any, diagnostics: Any | None, captured_at: str) -> dict[str, Any]:
    """Construye el payload §8 a partir de un ``Computer``."""
    from src.models.computer import Computer

    assert isinstance(computer, Computer)

    hardware_ids = computer.hardware_ids or {
        "system_uuid": None,
        "board_serial": None,
        "bios_serial": None,
        "chassis_serial": None,
        "nic_mac": None,
        "machine_guid": None,
    }

    computer_block = {
        "device_name": _truncate(computer.device_name, 64),
        "user_name": _truncate(computer.user_name, 128),
        "machine_mac": computer.machine_mac,
        "machine_ip": computer.machine_ip,
        "mobo_mark": _truncate(computer.mobo_mark, 128),
        "mobo_model": _truncate(computer.mobo_model, 128),
        "cpu_info": _truncate(computer.cpu_info, 200),
        "operative_system": _truncate(computer.operative_system, 100),
        "storage_model": _truncate(computer.storage_model, 128),
        "storage_cap": computer.storage_cap,
        "anydesk_id": computer.anydesk_id,
    }

    dimm_list = []
    for dimm in computer.dimm_list:
        dimm_list.append(
            {
                "caption": _truncate(dimm.caption, 128),
                "manufacturer": _truncate(dimm.manufacturer, 128),
                "part_number": _truncate(dimm.part_number, 128),
                "model": _truncate(dimm.model, 128),
                "tag": _truncate(dimm.tag, 128),
                "bank_label": _truncate(dimm.bank_label, 128),
                "device_locator": _truncate(dimm.device_locator, 128),
                "capacity": dimm.capacity,
                "speed": dimm.speed,
                "configured_clock_speed": dimm.configured_clock_speed,
                "configured_voltage": dimm.configured_voltage,
            }
        )

    storage_list = [drive.to_dictionary() for drive in computer.storage_list]

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "agent_version": AGENT_VERSION,
        "captured_at": captured_at,
        "device_uuid": computer.device_uuid,
        "identity_source": computer.identity_source,
        "hardware_ids": hardware_ids,
        "computer": computer_block,
        "dimm_list": dimm_list,
        "storage_list": storage_list,
        "storage_count": computer.storage_count,
    }

    if _env_bool("SYNC_SEND_DIAGNOSTICS", True) and diagnostics is not None:
        try:
            payload["diagnostics"] = diagnostics.as_dict()
        except Exception:  # noqa: BLE001
            payload["diagnostics"] = None

    return payload


def idempotency_key(device_uuid: str | None, captured_at: str) -> str:
    seed = f"{device_uuid or ''}|{captured_at}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


@dataclass
class SendResult:
    status: str  # synced | pending | failed_permanent
    remote_id: int | None = None
    error: str | None = None
    retry_after: float | None = None


class ApiClient:
    def __init__(self) -> None:
        self.endpoint = _env("SYNC_ENDPOINT")
        self.health_path = _env("SYNC_HEALTH_PATH")
        self.timeout = _env_int("SYNC_TIMEOUT", 10)
        self.connect_timeout = _env_int("SYNC_CONNECT_TIMEOUT", 3)
        self.retries = _env_int("SYNC_RETRIES", 2)
        self.backoff_base = float(_env("SYNC_BACKOFF_BASE", "1.0") or "1.0")
        self.verify_tls = _env_bool("SYNC_VERIFY_TLS", True)
        self.ca_bundle = _env("SYNC_CA_BUNDLE")
        self.auth_mode = _env("SYNC_AUTH", "api_key") or "api_key"
        self.api_key_header = _env("SYNC_API_KEY_HEADER", "X-Api-Key")
        self.api_key = _env("SYNC_API_KEY")
        self.token = _env("SYNC_TOKEN")
        self.basic_user = _env("SYNC_BASIC_USER")
        self.basic_password = _env("SYNC_BASIC_PASSWORD")
        self.user_agent = _env("SYNC_USER_AGENT", "TechnicalSheet/1.0")

    @property
    def enabled(self) -> bool:
        return _env_bool("SYNC_ENABLED", False) and bool(self.endpoint)

    def _ssl_context(self) -> ssl.SSLContext | None:
        if not self.endpoint.lower().startswith("https://"):
            return None
        if not self.verify_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx
        if self.ca_bundle:
            return ssl.create_default_context(cafile=self.ca_bundle)
        return ssl.create_default_context()

    def _headers(self, idempotency: str) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "Idempotency-Key": idempotency,
        }
        if self.auth_mode == "api_key" and self.api_key:
            headers[self.api_key_header] = self.api_key
        elif self.auth_mode == "bearer" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.auth_mode == "basic" and self.basic_user:
            import base64

            creds = base64.b64encode(
                f"{self.basic_user}:{self.basic_password}".encode("utf-8")
            ).decode("ascii")
            headers["Authorization"] = f"Basic {creds}"
        return headers

    def send(self, payload: dict[str, Any], remote_id: int | None = None) -> SendResult:
        if not self.endpoint:
            return SendResult(status="pending", error="SYNC_ENDPOINT vacío")

        captured_at = payload.get("captured_at") or ""
        device_uuid = payload.get("device_uuid")
        key = idempotency_key(device_uuid, captured_at)

        if remote_id:
            url = f"{self.endpoint.rstrip('/')}/{remote_id}"
            method = "PUT"
        else:
            url = self.endpoint.rstrip("/")
            method = "POST"

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = self._headers(key)

        last_error: str | None = None
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(
                    req, timeout=self.timeout, context=self._ssl_context()
                ) as response:
                    status_code = response.getcode()
                    body = response.read().decode("utf-8", errors="replace")
                    parsed = {}
                    try:
                        parsed = json.loads(body) if body else {}
                    except json.JSONDecodeError:
                        parsed = {}
                    if status_code in (200, 201, 204):
                        rid = parsed.get("id") or parsed.get("remote_id") or remote_id
                        # 409 already_exists handling is done on HTTPError path.
                        return SendResult(status="synced", remote_id=rid)
                    # Tratar otros 2xx como synced.
                    return SendResult(status="synced", remote_id=remote_id)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                parsed = {}
                try:
                    parsed = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    parsed = {}
                code = exc.code
                if code == 409:
                    err_code = parsed.get("error") or parsed.get("code")
                    if err_code == "already_exists":
                        existing_id = parsed.get("existing_id") or parsed.get("id")
                        if existing_id and not remote_id:
                            # Reintentar inmediatamente como PUT.
                            return self.send(payload, remote_id=existing_id)
                        return SendResult(status="synced", remote_id=existing_id or remote_id)
                    if err_code == "stale_capture":
                        return SendResult(status="synced", remote_id=remote_id)
                if code in (400, 422):
                    return SendResult(status="failed_permanent", error=f"HTTP {code}: {body[:200]}")
                if code in (401, 403):
                    return SendResult(status="failed_permanent", error=f"HTTP {code}: credenciales inválidas")
                if code == 404:
                    return SendResult(status="failed_permanent", error=f"HTTP {code}: endpoint no encontrado")
                if code in (408, 429) or code >= 500:
                    retry_after = None
                    ra = exc.headers.get("Retry-After") if exc.headers else None
                    if ra:
                        try:
                            retry_after = float(ra)
                        except ValueError:
                            retry_after = None
                    last_error = f"HTTP {code}"
                    # backoff y reintento
                    if attempt < self.retries:
                        delay = retry_after if retry_after is not None else self.backoff_base * (2 ** attempt)
                        time.sleep(min(delay, 10.0))
                        continue
                    return SendResult(status="pending", error=last_error, retry_after=retry_after)
                return SendResult(status="failed_permanent", error=f"HTTP {code}: {body[:200]}")
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < self.retries:
                    time.sleep(self.backoff_base * (2 ** attempt))
                    continue
                return SendResult(status="pending", error=last_error)

        return SendResult(status="pending", error=last_error or "sin respuesta")


class SyncManager:
    def __init__(self, repo: Any, diagnostics: Any | None = None) -> None:
        self.repo = repo
        self.client = ApiClient()
        self.diagnostics = diagnostics

    def sync_pending(self, max_items: int | None = None) -> dict[str, int]:
        if not self.client.enabled:
            return {"synced": 0, "pending": 0, "failed": 0, "skipped": 1}

        if max_items is None:
            max_items = _env_int("SYNC_MAX_ITEMS_PER_RUN", 50)

        pending = self.repo.read_pending_sync(limit=max_items)
        synced = 0
        failed = 0
        pending_count = 0

        for computer in pending:
            captured_at = computer.captured_at
            if not captured_at:
                from datetime import datetime, timezone

                captured_at = datetime.now(timezone.utc).isoformat()
                computer.captured_at = captured_at

            payload = build_payload(computer, self.diagnostics, captured_at)
            remote_id = getattr(computer, "remote_id", None)
            # Read remote_id from repo? Computer doesn't have it; query not available.
            # We'll pass None; repo tracks remote_id separately. For updates we need it.
            # Attempt to read from DB row via repo if method exists.
            result = self.client.send(payload, remote_id=remote_id)

            if result.status == "synced":
                self.repo.mark_sync_result(
                    computer.machine_mac, "synced", result.remote_id, None, captured_at
                )
                synced += 1
            elif result.status == "failed_permanent":
                self.repo.mark_sync_result(
                    computer.machine_mac, "failed_permanent", result.remote_id, result.error, captured_at
                )
                failed += 1
            else:
                self.repo.mark_sync_result(
                    computer.machine_mac, "pending", result.remote_id, result.error, captured_at
                )
                pending_count += 1

        return {"synced": synced, "pending": pending_count, "failed": failed, "skipped": 0}

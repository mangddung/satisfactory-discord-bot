import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ServerAPIError(Exception):
    """Print-friendly API error"""
    pass


def gen_token(url, password, timeout=5, privilege="Administrator"):
    stage = "PasswordLogin"
    try:
        resp = requests.post(
            url,
            json={
                "function": "PasswordLogin",
                "data": {
                    "Password": password,
                    "MinimumPrivilegeLevel": privilege
                }
            },
            verify=False,
            timeout=timeout
        )
        resp.raise_for_status()

        # JSON parsing
        try:
            payload = resp.json()
        except ValueError:
            raise ServerAPIError(f"[{stage}] invalid_json")

        # API error message process
        err = (payload.get("errorCode") or payload.get("error") or "").strip()
        if err:
            if err == "wrong_password":
                raise ServerAPIError(f"[{stage}] wrong_password: {privilege} password incorrect")
            raise ServerAPIError(f"[{stage}] {err}")

        data = payload.get("data") or {}
        token = data.get("authenticationToken") or data.get("AuthenticationToken")
        if not token:
            raise ServerAPIError(f"[{stage}] missing_token")

        return token

    except Timeout:
        raise ServerAPIError(f"[{stage}] timeout")
    except ConnectionError:
        raise ServerAPIError(f"[{stage}] connection_error")
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else "error"
        raise ServerAPIError(f"[{stage}] http_{status}")
    except RequestException:
        raise ServerAPIError(f"[{stage}] request_error")


def get_server_status(url, token, timeout=5):
    stage = "QueryServerState"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    try:
        resp = requests.post(
            url,
            json={"function": "QueryServerState", "data": {}},
            headers=headers,
            verify=False,
            timeout=timeout
        )
        resp.raise_for_status()

        try:
            payload = resp.json()
        except ValueError:
            raise ServerAPIError(f"[{stage}] invalid_json")

        # API error message process
        err = (payload.get("errorCode") or payload.get("error") or "").strip()
        if err:
            raise ServerAPIError(f"[{stage}] {err}")

        data = payload.get("data") or {}
        sgs = data.get("serverGameState")
        if sgs is None:
            raise ServerAPIError(f"[{stage}] missing_serverGameState")

        return sgs

    except Timeout:
        raise ServerAPIError(f"[{stage}] timeout")
    except ConnectionError:
        raise ServerAPIError(f"[{stage}] connection_error")
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else "error"
        raise ServerAPIError(f"[{stage}] http_{status}")
    except RequestException:
        raise ServerAPIError(f"[{stage}] request_error")

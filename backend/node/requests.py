import requests
from fastapi.responses import Response
from backend.logger import logger


class NodeRequests:
    """Handles requests to the node API."""

    def __init__(
        self,
        address: str,
        port: int,
        api_key: str,
        tunnel_address: str = "ovpanel.com",
        protocol: str = "tcp",
        ovpn_port: int = 1194,
        set_new_setting: bool = False,
    ):
        self.address = f"{address}:{port}"
        self.headers = {"key": api_key}
        self.tunnel_address = tunnel_address
        self.protocol = protocol
        self.ovpn_port = ovpn_port
        self.set_new_setting = set_new_setting
        self.last_error = ""

    def check_node(self) -> bool:
        """Checks the node status and sets new settings if necesary."""
        ok, _ = self.check_node_with_error()
        return ok

    def check_node_with_error(self) -> tuple[bool, str]:
        """Checks the node status and keeps the node's error message for callers."""
        api = f"http://{self.address}/sync/status"
        try:
            data = {
                "tunnel_address": self.tunnel_address,
                "protocol": self.protocol,
                "ovpn_port": self.ovpn_port,
                "set_new_setting": self.set_new_setting,
            }
            response = requests.get(
                api, headers=self.headers, json=data, timeout=10
            )
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            if response.status_code == 200 and payload.get("success"):
                self.last_error = ""
                return True, ""

            msg = payload.get("msg") or response.reason or "Node health check failed"
            self.last_error = f"{response.status_code}: {msg}"
            logger.error(f"Node {self.address} health check failed: {self.last_error}")
            return False, self.last_error
        except requests.exceptions.Timeout:
            self.last_error = "Timed out while checking node"
        except requests.exceptions.ConnectionError as e:
            self.last_error = f"Connection error while checking node: {e}"
        except Exception as e:
            self.last_error = f"Error checking node: {e}"

        logger.error(f"Error checking node {self.address}: {self.last_error}")
        return False, self.last_error

    def get_node_info(self) -> dict:
        api = f"http://{self.address}/sync/status"
        try:
            data = {
                "tunnel_address": self.tunnel_address,
                "protocol": self.protocol,
                "ovpn_port": self.ovpn_port,
                "set_new_setting": self.set_new_setting,
            }
            response = requests.get(
                api, headers=self.headers, json=data, timeout=10
            ).json()
            if response.get("success"):
                return response.get("data")
            else:
                logger.error(
                    f"Failed to get node info on {self.address}: {response.get('msg')}"
                )
                return {}
        except Exception as e:
            logger.error(f"Error getting node info on {self.address}: {e}")
            return {}

    def create_user(self, name: str) -> bool:
        ok, _ = self.create_user_with_error(name)
        return ok

    def create_user_with_error(self, name: str) -> tuple[bool, str]:
        api = f"http://{self.address}/sync/user"
        data = {"name": name}
        try:
            response = requests.post(
                api, headers=self.headers, json=data, timeout=25
            )
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            if response.status_code == 200 and payload.get("success"):
                return True, ""

            msg = payload.get("msg") or response.reason or "Node rejected user creation"
            error = f"{response.status_code}: {msg}"
            logger.error(f"Failed to create user on node {self.address}: {error}")
            return False, error
        except Exception as e:
            logger.error(f"Error creating user on node {self.address}: {e}")
            return False, str(e)

    def change_user_status(self, name, status):
        api = f"http://{self.address}/sync/user"
        try:
            data = {"name": name, "status": "activate" if status else "deactivate"}
            response = requests.put(
                api, headers=self.headers, json=data, timeout=10
            ).json()

            if response.get("success"):
                return True
            else:
                logger.error(
                    f"Failed to change user status on node {self.address}: {response.get('msg')}"
                )
                return False
        except Exception as e:
            logger.error(f"Error change user status on node {self.address}: {e}")
            return False

    def download_ovpn_client(self, name: str) -> Response:
        api = f"http://{self.address}/sync/download/ovpn/{name}"
        try:
            response = requests.get(api, headers=self.headers, timeout=25)
            content_type = response.headers.get("content-type", "")
            if (
                response.status_code == 200
                and response.content
                and "application/json" not in content_type
            ):
                return Response(
                    content=response.content,
                    media_type="application/x-openvpn-profile",
                    headers={
                        "Content-Disposition": f"attachment; filename={name}.ovpn"
                    },
                )
            logger.error(
                f"Failed to download OVPN client '{name}' from node {self.address}: "
                f"{response.status_code} {response.text[:200]}"
            )
        except Exception as e:
            logger.error(f"Error downloading OVPN client from node {self.address}: {e}")
        return None

    def delete_user(self, name: str) -> bool:
        api = f"http://{self.address}/sync/user/{name}"
        try:
            response = requests.delete(
                api, headers=self.headers, timeout=25
            ).json()
            if response.get("success"):
                return True
            else:
                logger.error(
                    f"Failed to delete user on node {self.address}: {response.get('msg')}"
                )
                return False
        except Exception as e:
            logger.error(f"Error deleting user on node {self.address}: {e}")
            return False

    def get_users_usage(self) ->dict | bool:
        api = f"http://{self.address}/sync/usage"
        try:
            response = requests.get(api, headers=self.headers, timeout=25).json()
            if response.get("success"):
                logger.info(f"get users usage on node {self.address}: {response.get('msg')}")
                return response.get("data")
            else:
                logger.error(
                    f"Failed to get users usage on node {self.address}: {response.get('msg')}"
                )
                return False
        except Exception as e:
            logger.error(f"Error when getting users usage on node {self.address}: {e}")
            return False

from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.logger import logger
from backend.schema._input import NodeCreate
from .requests import NodeRequests
from backend.db import crud
from backend.db.models import Node


def openvpn_client_name(user_name: str, node_name: str) -> str:
    return f"{user_name}-{node_name}"


async def add_node_handler(request: NodeCreate, db: Session) -> tuple[bool, str]:
    new_node = NodeRequests(
        request.address,
        request.port,
        request.key,
        request.tunnel_address,
        request.protocol,
        request.ovpn_port,
        request.set_new_setting,
    )
    node_ok, error = new_node.check_node_with_error()
    if not node_ok:
        msg = f"Node health check failed: {error}"
        logger.warning(f"Failed to add node {request.address}:{request.port}: {msg}")
        return False, msg

    try:
        saved_node = crud.create_node(db, request)
        logger.info(f"Node added successfully: {request.address}:{request.port}")
        return True, f"Node added successfully with id {saved_node.id}"
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save node {request.address}:{request.port}: {e}")
        return False, f"Node health check passed, but database save failed: {e}"


async def update_node_handler(node_id: int, request: NodeCreate, db: Session) -> bool:
    """Update a node"""
    crud.update_node(db, node_id, request)
    restart_node = NodeRequests(
        address=request.address,
        port=request.port,
        api_key=request.key,
        tunnel_address=request.tunnel_address,
        protocol=request.protocol,
        ovpn_port=request.ovpn_port,
        set_new_setting=True,
    ).check_node()

    logger.info(f"Node updated successfully: {request.address}:{request.port}")
    return restart_node


async def delete_node_handler(node_id: int, db: Session) -> bool:
    """Delete a node"""
    node = crud.get_node_by_id(db, node_id)
    if node:
        crud.delete_node(db, node.id)
        logger.info(f"Node deleted successfully: {node.name}")
        return True
    else:
        logger.warning(f"Failed to delete node: {node.name}")
        return False


async def list_nodes_handler(db: Session) -> list:
    """Retrieve all nodes"""
    nodes_list = []
    nodes = crud.get_all_nodes(db)
    for node in nodes:
        node_info = {
            "id": node.id,
            "name": node.name,
            "address": node.address,
            "tunnel-address": node.tunnel_address,
            "ovpn_port": node.ovpn_port,
            "protocol": node.protocol,
            "port": node.port,
            "status": node.status,
        }
        nodes_list.append(node_info)
    return nodes_list


async def get_node_status_handler(node_id: int, db: Session):
    """Get the status of a node"""
    node = crud.get_node_by_id(db, node_id)
    if node:
        node_status = NodeRequests(
            address=node.address, port=node.port, api_key=node.key
        ).get_node_info()
        print(node_status)
        return {
            "address": node.address,
            "port": node.port,
            "status": "active" if node.status else "inactive",
            "node_info": node_status,
        }
    return None


async def create_user_on_all_nodes(name: str, db: Session):
    """Create a user on all nodes"""
    nodes = crud.get_all_nodes(db)
    if not nodes:
        return False, "No nodes are configured"

    errors = []
    for node in nodes:
        client_name = openvpn_client_name(name, node.name)
        node_requests = NodeRequests(
            address=node.address, port=node.port, api_key=node.key
        )
        node_status, status_error = node_requests.check_node_with_error()
        if node_status:
            created, create_error = node_requests.create_user_with_error(client_name)
            if created:
                logger.info(
                    f"User '{client_name}' created on node {node.address}:{node.port}"
                )
                continue
            errors.append(f"{node.name}: {create_error}")
            logger.warning(
                f"Failed to create user '{client_name}' on node {node.address}:{node.port}: {create_error}"
            )
        else:
            errors.append(f"{node.name}: {status_error}")
            logger.warning(
                f"Failed to create user '{client_name}' on node {node.address}:{node.port}: {status_error}"
            )

    if errors:
        return False, "Failed to create user on node(s): " + "; ".join(errors)
    return True, "User created on all nodes"


async def change_user_status_on_all_nodes(
    uuid: str, name: str, status: bool, db: Session
):
    nodes = crud.get_all_nodes(db)
    crud.change_user_status(db, uuid, status)

    if nodes:
        for node in nodes:
            node_request = NodeRequests(
                address=node.address, port=node.port, api_key=node.key
            )
            node_status = node_request.check_node()
            if node_status:
                client_name = openvpn_client_name(name, node.name)
                node_request.change_user_status(client_name, status)
                logger.info(
                    f"User '{client_name}' changed status on node {node.address}:{node.port}"
                )
            else:
                logger.warning(
                    f"Failed to chang user status '{openvpn_client_name(name, node.name)}' on node {node.address}:{node.port}"
                )


async def download_ovpn_client_from_node(
    uuid: str, node_id: int, db: Session
) -> Response | None:
    """Download OVPN client from a node"""
    node = crud.get_node_by_id(db, node_id)
    user = crud.get_user_by_uuid(db, uuid)
    if not node or not user:
        return None
    client_name = openvpn_client_name(user.name, node.name)
    result = NodeRequests(
        address=node.address, port=node.port, api_key=node.key
    ).download_ovpn_client(client_name)
    if result:
        logger.info(
            f"OVPN client downloaded for user '{client_name}' on node {node.address}:{node.port}"
        )
        return result
    return None


async def delete_user_on_all_nodes(name: str, db: Session) -> bool:
    """Delete a user from all nodes"""
    nodes = crud.get_all_nodes(db)
    if nodes:
        for node in nodes:
            node_requests = NodeRequests(
                address=node.address, port=node.port, api_key=node.key
            )
            node_status = node_requests.check_node()
            if node_status:
                client_name = openvpn_client_name(name, node.name)
                node_requests.delete_user(client_name)
                logger.info(
                    f"User '{client_name}' deleted on node {node.address}:{node.port}"
                )
            else:
                logger.warning(
                    f"Failed to delete user '{openvpn_client_name(name, node.name)}' on node {node.address}:{node.port}"
                )
        return True
    return False


async def get_users_used_traffic(node: Node, db: Session) -> dict:
    """Geting users usage on node"""
    node_requests = NodeRequests(address=node.address, port=node.port, api_key=node.key)
    response = node_requests.get_users_usage()

    if not response:
        return {}
    return response.get("users", {})

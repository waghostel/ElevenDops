"""
Collection Builder Component for Postman Testing

Builds Postman collections programmatically with folders, requests, and test scripts.
Generates valid Postman collection JSON.

Requirements: 12.1, 12.2, 12.3
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CollectionBuilder:
    """
    Builds Postman collections programmatically.
    
    Supports:
    - Creating collections
    - Adding folders
    - Adding requests
    - Adding test scripts
    - Adding pre-request scripts
    - Building valid Postman collection JSON
    """
    
    def __init__(self, workspace_id: str, name: str = "Test Collection"):
        """
        Initialize CollectionBuilder.
        
        Args:
            workspace_id: Postman workspace ID
            name: Collection name
        """
        self.workspace_id = workspace_id
        self.name = name
        self.collection_id = f"col_{uuid.uuid4().hex[:16]}"
        self.collection_uid = uuid.uuid4().hex
        self.folders: Dict[str, Dict[str, Any]] = {}
        self.requests: Dict[str, Dict[str, Any]] = {}
        self.variables: Dict[str, Any] = {}
        self.auth: Optional[Dict[str, Any]] = None
        self.created_at = datetime.utcnow().isoformat()
        self.description = ""
    
    def create_collection(
        self,
        name: str,
        description: str = "",
        auth: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            description: Collection description
            auth: Authentication configuration
            
        Returns:
            Collection metadata
        """
        self.name = name
        self.description = description
        self.auth = auth
        
        metadata = {
            "id": self.collection_id,
            "uid": self.collection_uid,
            "name": name,
            "description": description,
            "workspace_id": self.workspace_id,
            "created_at": self.created_at,
            "folder_count": len(self.folders),
            "request_count": len(self.requests),
        }
        
        logger.info(f"Created collection: {name} ({self.collection_id})")
        return metadata
    
    def add_folder(
        self,
        folder_name: str,
        parent_folder: Optional[str] = None,
        description: str = "",
    ) -> str:
        """
        Add folder to collection.
        
        Args:
            folder_name: Folder name
            parent_folder: Parent folder name (for nesting)
            description: Folder description
            
        Returns:
            Folder ID
        """
        folder_id = f"folder_{uuid.uuid4().hex[:16]}"
        
        self.folders[folder_id] = {
            "id": folder_id,
            "name": folder_name,
            "description": description,
            "parent": parent_folder,
            "requests": [],
            "created_at": datetime.utcnow().isoformat(),
        }
        
        logger.debug(f"Added folder: {folder_name} ({folder_id})")
        return folder_id
    
    def add_request(
        self,
        folder_id: str,
        name: str,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        description: str = "",
    ) -> str:
        """
        Add request to folder.
        
        Args:
            folder_id: Folder ID
            name: Request name
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            body: Request body
            headers: Request headers
            params: Query parameters
            description: Request description
            
        Returns:
            Request ID
        """
        if folder_id not in self.folders:
            raise ValueError(f"Folder {folder_id} not found")
        
        request_id = f"req_{uuid.uuid4().hex[:16]}"
        
        # Build request structure
        request_data = {
            "id": request_id,
            "name": name,
            "method": method.upper(),
            "url": url,
            "description": description,
            "headers": headers or {},
            "params": params or {},
            "body": body,
            "tests": [],
            "pre_request_script": None,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self.requests[request_id] = request_data
        self.folders[folder_id]["requests"].append(request_id)
        
        logger.debug(f"Added request: {name} ({method} {url})")
        return request_id
    
    def add_test_script(
        self,
        request_id: str,
        test_script: str,
        description: str = "",
    ) -> None:
        """
        Add test script to request.
        
        Args:
            request_id: Request ID
            test_script: JavaScript test script
            description: Script description
        """
        if request_id not in self.requests:
            raise ValueError(f"Request {request_id} not found")
        
        self.requests[request_id]["tests"].append({
            "script": test_script,
            "description": description,
            "added_at": datetime.utcnow().isoformat(),
        })
        
        logger.debug(f"Added test script to request: {request_id}")
    
    def add_pre_request_script(
        self,
        request_id: str,
        script: str,
        description: str = "",
    ) -> None:
        """
        Add pre-request script to request.
        
        Args:
            request_id: Request ID
            script: JavaScript pre-request script
            description: Script description
        """
        if request_id not in self.requests:
            raise ValueError(f"Request {request_id} not found")
        
        self.requests[request_id]["pre_request_script"] = {
            "script": script,
            "description": description,
            "added_at": datetime.utcnow().isoformat(),
        }
        
        logger.debug(f"Added pre-request script to request: {request_id}")
    
    def add_collection_variable(
        self,
        key: str,
        value: str,
        enabled: bool = True,
        description: str = "",
    ) -> None:
        """
        Add collection variable.
        
        Args:
            key: Variable key
            value: Variable value
            enabled: Whether variable is enabled
            description: Variable description
        """
        self.variables[key] = {
            "key": key,
            "value": value,
            "enabled": enabled,
            "type": "string",
            "description": description,
        }
        
        logger.debug(f"Added collection variable: {key}")
    
    def set_auth(
        self,
        auth_type: str,
        credentials: Dict[str, Any],
    ) -> None:
        """
        Set collection authentication.
        
        Args:
            auth_type: Authentication type (bearer, basic, oauth2, etc.)
            credentials: Authentication credentials
        """
        self.auth = {
            "type": auth_type,
            "credentials": credentials,
        }
        
        logger.debug(f"Set collection auth: {auth_type}")
    
    def build(self) -> Dict[str, Any]:
        """
        Build valid Postman collection JSON.
        
        Returns:
            Postman collection JSON structure
        """
        # Build items (folders and requests)
        items = []
        
        for folder_id, folder in self.folders.items():
            folder_items = []
            
            # Add requests to folder
            for request_id in folder["requests"]:
                if request_id in self.requests:
                    request = self.requests[request_id]
                    folder_items.append(self._build_request_item(request))
            
            # Add folder to items
            items.append({
                "name": folder["name"],
                "description": folder["description"],
                "item": folder_items,
            })
        
        # Build collection structure
        collection = {
            "info": {
                "name": self.name,
                "description": self.description,
                "_postman_id": self.collection_uid,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": items,
            "variable": [
                {
                    "key": var["key"],
                    "value": var["value"],
                    "type": var.get("type", "string"),
                    "disabled": not var["enabled"],
                }
                for var in self.variables.values()
            ],
            "auth": self.auth,
            "event": [],
        }
        
        logger.info(f"Built collection: {self.name} with {len(items)} folders")
        return collection
    
    def _build_request_item(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build request item for collection.
        
        Args:
            request: Request data
            
        Returns:
            Request item structure
        """
        # Build request body
        body = None
        if request.get("body"):
            body = {
                "mode": "raw",
                "raw": json.dumps(request["body"]),
                "options": {
                    "raw": {
                        "language": "json",
                    }
                }
            }
        
        # Build headers
        headers = []
        for key, value in request.get("headers", {}).items():
            headers.append({
                "key": key,
                "value": value,
                "type": "text",
            })
        
        # Build query parameters
        query = []
        for key, value in request.get("params", {}).items():
            query.append({
                "key": key,
                "value": value,
                "type": "text",
            })
        
        # Build test scripts
        test_script = None
        if request.get("tests"):
            test_code = "\n".join([t["script"] for t in request["tests"]])
            test_script = {
                "type": "text/javascript",
                "exec": test_code.split("\n"),
            }
        
        # Build pre-request script
        pre_request_script = None
        if request.get("pre_request_script"):
            pre_request_script = {
                "type": "text/javascript",
                "exec": request["pre_request_script"]["script"].split("\n"),
            }
        
        # Build request item
        item = {
            "name": request["name"],
            "description": request.get("description", ""),
            "request": {
                "method": request["method"],
                "header": headers,
                "body": body,
                "url": {
                    "raw": request["url"],
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "8000",
                    "path": request["url"].split("/")[3:],
                    "query": query,
                },
            },
            "response": [],
        }
        
        # Add scripts if present
        if test_script or pre_request_script:
            item["event"] = []
            if pre_request_script:
                item["event"].append({
                    "listen": "prerequest",
                    "script": pre_request_script,
                })
            if test_script:
                item["event"].append({
                    "listen": "test",
                    "script": test_script,
                })
        
        return item
    
    def to_json(self) -> str:
        """
        Convert collection to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.build(), indent=2)
    
    def get_folder_count(self) -> int:
        """
        Get number of folders in collection.
        
        Returns:
            Folder count
        """
        return len(self.folders)
    
    def get_request_count(self) -> int:
        """
        Get number of requests in collection.
        
        Returns:
            Request count
        """
        return len(self.requests)
    
    def get_variable_count(self) -> int:
        """
        Get number of variables in collection.
        
        Returns:
            Variable count
        """
        return len(self.variables)
    
    def get_folder_ids(self) -> List[str]:
        """
        Get all folder IDs.
        
        Returns:
            List of folder IDs
        """
        return list(self.folders.keys())
    
    def get_request_ids(self) -> List[str]:
        """
        Get all request IDs.
        
        Returns:
            List of request IDs
        """
        return list(self.requests.keys())
    
    def get_requests_in_folder(self, folder_id: str) -> List[str]:
        """
        Get request IDs in a folder.
        
        Args:
            folder_id: Folder ID
            
        Returns:
            List of request IDs
        """
        if folder_id not in self.folders:
            return []
        
        return self.folders[folder_id]["requests"]
    
    def validate_collection(self) -> bool:
        """
        Validate collection structure.
        
        Returns:
            True if collection is valid
        """
        # Check required fields
        if not self.name:
            logger.warning("Collection name is empty")
            return False
        
        if not self.collection_id:
            logger.warning("Collection ID is empty")
            return False
        
        # Check that all requests are in folders
        requests_in_folders = set()
        for folder in self.folders.values():
            requests_in_folders.update(folder["requests"])
        
        orphaned_requests = set(self.requests.keys()) - requests_in_folders
        if orphaned_requests:
            logger.warning(f"Orphaned requests: {orphaned_requests}")
            return False
        
        logger.info("Collection validation passed")
        return True
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CollectionBuilder(name={self.name}, "
            f"folders={len(self.folders)}, "
            f"requests={len(self.requests)}, "
            f"id={self.collection_id})"
        )


__all__ = ["CollectionBuilder"]

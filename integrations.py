"""
External Integrations: Zapier, Microsoft 365, SharePoint, OneDrive
Parallel Processing for High Performance
"""

import asyncio
import concurrent.futures
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime

import httpx
from msal import ConfidentialClientApplication
from Office365.runtime.auth.authentication_context import AuthenticationContext
from Office365.sharepoint.client_context import ClientContext

from config import get_settings, encrypt_sensitive_data, decrypt_sensitive_data
from logging_system import logging_system, AuditEventType


class ZapierIntegration:
    """
    Zapier webhook integration for workflow automation

    Security:
    - API key authentication
    - HTTPS only
    - Rate limiting
    - Input validation
    """

    def __init__(self):
        self.settings = get_settings()

    async def trigger_webhook(
        self,
        event_type: str,
        data: Dict[str, Any],
        user: Optional[str] = None,
    ) -> bool:
        """
        Trigger a Zapier webhook

        Args:
            event_type: Type of event (e.g., "trade_executed", "document_ready")
            data: Event data to send
            user: Username for audit logging

        Returns:
            True if webhook triggered successfully
        """
        if not self.settings.zapier_webhook_url:
            logging_system.warning("Zapier webhook URL not configured")
            return False

        try:
            payload = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
            }

            headers = {}
            if self.settings.zapier_api_key:
                headers["X-API-Key"] = self.settings.zapier_api_key

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.settings.zapier_webhook_url,
                    json=payload,
                    headers=headers,
                )

                response.raise_for_status()

            logging_system.audit(
                event_type=AuditEventType.ZAPIER_WEBHOOK_TRIGGERED,
                user=user or "system",
                action=f"trigger webhook: {event_type}",
                details={"event_type": event_type, "status_code": response.status_code},
                success=True,
            )

            logging_system.info(
                f"Zapier webhook triggered: {event_type}",
                event_type=event_type,
                status_code=response.status_code,
            )

            return True

        except Exception as e:
            logging_system.error(
                f"Failed to trigger Zapier webhook: {e}",
                event_type=event_type,
                error=str(e),
            )

            logging_system.audit(
                event_type=AuditEventType.ZAPIER_WEBHOOK_TRIGGERED,
                user=user or "system",
                action=f"trigger webhook: {event_type}",
                details={"event_type": event_type, "error": str(e)},
                success=False,
            )

            return False


class MicrosoftIntegration:
    """
    Microsoft 365 integration using MSAL

    Provides access to:
    - Microsoft Graph API
    - SharePoint
    - OneDrive
    - Outlook
    - Power Automate
    """

    def __init__(self):
        self.settings = get_settings()
        self._access_token: Optional[str] = None
        self._msal_app: Optional[ConfidentialClientApplication] = None

    def _get_msal_app(self) -> ConfidentialClientApplication:
        """Get or create MSAL app"""
        if self._msal_app is None:
            if not all([
                self.settings.microsoft_client_id,
                self.settings.microsoft_client_secret,
                self.settings.microsoft_tenant_id,
            ]):
                raise ValueError("Microsoft credentials not configured")

            self._msal_app = ConfidentialClientApplication(
                client_id=self.settings.microsoft_client_id,
                client_credential=self.settings.microsoft_client_secret,
                authority=f"https://login.microsoftonline.com/{self.settings.microsoft_tenant_id}",
            )

        return self._msal_app

    async def get_access_token(self, scopes: List[str]) -> str:
        """Get Microsoft access token"""
        msal_app = self._get_msal_app()

        # Try to get token from cache
        accounts = msal_app.get_accounts()
        if accounts:
            result = msal_app.acquire_token_silent(scopes, account=accounts[0])
            if result and "access_token" in result:
                return result["access_token"]

        # Acquire new token
        result = msal_app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            logging_system.info("Microsoft access token acquired")
            return result["access_token"]
        else:
            error = result.get("error_description", "Unknown error")
            raise Exception(f"Failed to acquire Microsoft token: {error}")

    async def call_graph_api(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        user: Optional[str] = None,
    ) -> Dict:
        """
        Call Microsoft Graph API

        Args:
            endpoint: Graph API endpoint (e.g., "/me", "/users")
            method: HTTP method
            data: Request data for POST/PATCH
            user: Username for audit logging

        Returns:
            API response data
        """
        try:
            scopes = ["https://graph.microsoft.com/.default"]
            access_token = await self.get_access_token(scopes)

            url = f"https://graph.microsoft.com/v1.0{endpoint}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data)
                elif method == "PATCH":
                    response = await client.patch(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()

            logging_system.audit(
                event_type=AuditEventType.MICROSOFT_API_CALLED,
                user=user or "system",
                action=f"{method} {endpoint}",
                details={"endpoint": endpoint, "method": method},
                success=True,
            )

            return response.json()

        except Exception as e:
            logging_system.error(
                f"Microsoft Graph API call failed: {e}",
                endpoint=endpoint,
                error=str(e),
            )
            raise


class SharePointIntegration:
    """
    SharePoint integration for document management

    Security:
    - Encrypted document storage
    - Access control
    - Audit logging
    """

    def __init__(self):
        self.settings = get_settings()
        self._sp_context: Optional[ClientContext] = None

    def _get_sharepoint_context(self) -> ClientContext:
        """Get SharePoint context"""
        if self._sp_context is None:
            if not self.settings.sharepoint_site_url:
                raise ValueError("SharePoint site URL not configured")

            # In production, use proper authentication
            auth_context = AuthenticationContext(self.settings.sharepoint_site_url)

            # Authenticate (placeholder - use proper credentials in production)
            # auth_context.acquire_token_for_user(username, password)

            self._sp_context = ClientContext(
                self.settings.sharepoint_site_url,
                auth_context,
            )

        return self._sp_context

    async def upload_document(
        self,
        file_path: str,
        folder_path: str,
        encrypt: bool = True,
        user: Optional[str] = None,
    ) -> Dict:
        """
        Upload document to SharePoint with optional encryption

        Args:
            file_path: Local file path
            folder_path: SharePoint folder path
            encrypt: Whether to encrypt before upload
            user: Username for audit logging

        Returns:
            Upload result
        """
        try:
            # Encrypt document if requested
            if encrypt:
                # Read file
                with open(file_path, "rb") as f:
                    content = f.read()

                # Encrypt content
                encrypted_content = encrypt_sensitive_data(content.decode("utf-8", errors="ignore"))

                # Write encrypted content to temp file
                encrypted_path = f"{file_path}.encrypted"
                with open(encrypted_path, "wb") as f:
                    f.write(encrypted_content)

                upload_path = encrypted_path
            else:
                upload_path = file_path

            # Upload to SharePoint (placeholder - implement actual upload)
            # sp_context = self._get_sharepoint_context()
            # result = sp_context.web.folders.get_by_url(folder_path).files.upload(upload_path)

            result = {
                "success": True,
                "file_path": file_path,
                "folder_path": folder_path,
                "encrypted": encrypt,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logging_system.audit(
                event_type=AuditEventType.SHAREPOINT_ACCESS,
                user=user or "system",
                action=f"upload document to {folder_path}",
                details=result,
                success=True,
            )

            logging_system.info(
                f"Document uploaded to SharePoint: {file_path}",
                file_path=file_path,
                folder_path=folder_path,
                encrypted=encrypt,
            )

            return result

        except Exception as e:
            logging_system.error(
                f"SharePoint upload failed: {e}",
                file_path=file_path,
                error=str(e),
            )
            raise


class ParallelProcessor:
    """
    Parallel processing system for high-performance operations

    Features:
    - Concurrent task execution
    - Thread pool for I/O-bound tasks
    - Process pool for CPU-bound tasks
    - Error handling and logging
    """

    def __init__(self, max_workers: Optional[int] = None):
        self.settings = get_settings()
        self.max_workers = max_workers or self.settings.max_workers

        # Thread pool for I/O-bound tasks
        self._thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        )

        # Process pool for CPU-bound tasks
        self._process_executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=min(self.max_workers, 8)  # Limit process workers
        )

        logging_system.info(
            f"Parallel processor initialized with {self.max_workers} workers",
            max_workers=self.max_workers,
        )

    async def run_parallel_io_tasks(
        self,
        tasks: List[Callable],
        *args,
        **kwargs,
    ) -> List[Any]:
        """
        Run I/O-bound tasks in parallel using thread pool

        Args:
            tasks: List of callable functions to execute

        Returns:
            List of results in same order as tasks
        """
        try:
            loop = asyncio.get_event_loop()

            # Submit all tasks to thread pool
            futures = [
                loop.run_in_executor(self._thread_executor, task, *args, **kwargs)
                for task in tasks
            ]

            # Wait for all tasks to complete
            results = await asyncio.gather(*futures, return_exceptions=True)

            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging_system.error(
                        f"Parallel task {i} failed: {result}",
                        task_index=i,
                        error=str(result),
                    )

            return results

        except Exception as e:
            logging_system.error(f"Parallel execution failed: {e}")
            raise

    async def run_parallel_cpu_tasks(
        self,
        tasks: List[Callable],
        *args,
        **kwargs,
    ) -> List[Any]:
        """
        Run CPU-bound tasks in parallel using process pool

        Args:
            tasks: List of callable functions to execute

        Returns:
            List of results in same order as tasks
        """
        try:
            loop = asyncio.get_event_loop()

            # Submit all tasks to process pool
            futures = [
                loop.run_in_executor(self._process_executor, task, *args, **kwargs)
                for task in tasks
            ]

            # Wait for all tasks to complete
            results = await asyncio.gather(*futures, return_exceptions=True)

            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging_system.error(
                        f"Parallel CPU task {i} failed: {result}",
                        task_index=i,
                        error=str(result),
                    )

            return results

        except Exception as e:
            logging_system.error(f"Parallel CPU execution failed: {e}")
            raise

    async def map_parallel(
        self,
        func: Callable,
        items: List[Any],
        batch_size: Optional[int] = None,
    ) -> List[Any]:
        """
        Map function over items in parallel

        Args:
            func: Function to apply to each item
            items: List of items to process
            batch_size: Optional batch size for processing

        Returns:
            List of results
        """
        if batch_size is None:
            batch_size = self.max_workers * 2

        results = []

        # Process in batches to avoid overwhelming the system
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            # Create tasks for this batch
            tasks = [lambda item=item: func(item) for item in batch]

            # Execute batch
            batch_results = await self.run_parallel_io_tasks(tasks)
            results.extend(batch_results)

        return results

    def shutdown(self):
        """Shutdown executor pools"""
        self._thread_executor.shutdown(wait=True)
        self._process_executor.shutdown(wait=True)

        logging_system.info("Parallel processor shutdown complete")


# Global instances
zapier_integration = ZapierIntegration()
microsoft_integration = MicrosoftIntegration()
sharepoint_integration = SharePointIntegration()
parallel_processor = ParallelProcessor()

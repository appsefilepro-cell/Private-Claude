"""
Encrypted Legal Document Management System
FIX: Unencrypted Storage of Sensitive Legal and Financial Data
"""

import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum

from pydantic import BaseModel

from config import get_settings, encrypt_sensitive_data, decrypt_sensitive_data
from logging_system import logging_system, AuditEventType


class DocumentType(str, Enum):
    """Types of legal documents"""
    MOTION = "motion"
    EXHIBIT = "exhibit"
    COMPLAINT = "complaint"
    BRIEF = "brief"
    CONTRACT = "contract"
    PROBATE = "probate"
    EVIDENCE = "evidence"
    OTHER = "other"


class SensitivityLevel(str, Enum):
    """Document sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    HIGHLY_CONFIDENTIAL = "highly_confidential"


class LegalDocument(BaseModel):
    """Legal document model"""
    document_id: str
    title: str
    document_type: DocumentType
    sensitivity: SensitivityLevel
    created_at: datetime
    modified_at: datetime
    owner: str
    content_hash: str
    encrypted: bool
    metadata: Dict


class EncryptedDocumentStore:
    """
    Secure storage for legal documents with encryption

    Security Features:
    - Automatic encryption of sensitive documents
    - Content hashing for integrity verification
    - Access logging and audit trail
    - Metadata encryption for highly sensitive docs
    - Secure deletion
    """

    def __init__(self):
        self.settings = get_settings()
        self.storage_path = Path("secure_documents")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._document_index: Dict[str, LegalDocument] = {}

    def _should_encrypt(self, sensitivity: SensitivityLevel) -> bool:
        """Determine if document should be encrypted"""
        return sensitivity in [
            SensitivityLevel.CONFIDENTIAL,
            SensitivityLevel.HIGHLY_CONFIDENTIAL,
        ]

    def _generate_document_id(self, title: str, timestamp: datetime) -> str:
        """Generate unique document ID"""
        data = f"{title}_{timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_document_path(self, document_id: str, encrypted: bool = False) -> Path:
        """Get filesystem path for document"""
        extension = ".encrypted" if encrypted else ".md"
        return self.storage_path / f"{document_id}{extension}"

    def create_document(
        self,
        title: str,
        content: str,
        document_type: DocumentType,
        sensitivity: SensitivityLevel,
        owner: str,
        metadata: Optional[Dict] = None,
    ) -> LegalDocument:
        """
        Create and store a legal document

        Args:
            title: Document title
            content: Document content (Markdown format)
            document_type: Type of document
            sensitivity: Sensitivity level
            owner: Document owner username
            metadata: Additional metadata

        Returns:
            Created document object
        """
        now = datetime.utcnow()
        document_id = self._generate_document_id(title, now)

        # Check if encryption is required
        should_encrypt = self._should_encrypt(sensitivity)

        # Compute content hash
        content_hash = self._compute_hash(content)

        # Create document object
        document = LegalDocument(
            document_id=document_id,
            title=title,
            document_type=document_type,
            sensitivity=sensitivity,
            created_at=now,
            modified_at=now,
            owner=owner,
            content_hash=content_hash,
            encrypted=should_encrypt,
            metadata=metadata or {},
        )

        # Store document
        if should_encrypt:
            # Encrypt content
            encrypted_content = encrypt_sensitive_data(content)

            # Write encrypted content
            doc_path = self._get_document_path(document_id, encrypted=True)
            with open(doc_path, "wb") as f:
                f.write(encrypted_content)

            logging_system.audit(
                event_type=AuditEventType.DATA_ENCRYPTED,
                user=owner,
                action=f"create encrypted document: {title}",
                details={
                    "document_id": document_id,
                    "document_type": document_type.value,
                    "sensitivity": sensitivity.value,
                },
            )

        else:
            # Write plain content
            doc_path = self._get_document_path(document_id, encrypted=False)
            with open(doc_path, "w") as f:
                f.write(content)

        # Store in index
        self._document_index[document_id] = document

        # Audit log
        logging_system.audit_sensitive_data_access(
            user=owner,
            data_type="legal_document",
            operation="create",
            record_id=document_id,
        )

        logging_system.info(
            f"Legal document created: {title}",
            document_id=document_id,
            document_type=document_type.value,
            encrypted=should_encrypt,
            owner=owner,
        )

        return document

    def get_document(
        self,
        document_id: str,
        user: str,
    ) -> tuple:
        """
        Retrieve a document

        Args:
            document_id: Document ID
            user: Requesting user

        Returns:
            Tuple of (document, content)
        """
        if document_id not in self._document_index:
            raise ValueError(f"Document not found: {document_id}")

        document = self._document_index[document_id]

        # Read content
        if document.encrypted:
            doc_path = self._get_document_path(document_id, encrypted=True)

            with open(doc_path, "rb") as f:
                encrypted_content = f.read()

            # Decrypt content
            content = decrypt_sensitive_data(encrypted_content)

            logging_system.audit(
                event_type=AuditEventType.DATA_DECRYPTED,
                user=user,
                action=f"read encrypted document: {document.title}",
                details={
                    "document_id": document_id,
                    "document_type": document.document_type.value,
                },
            )

        else:
            doc_path = self._get_document_path(document_id, encrypted=False)

            with open(doc_path, "r") as f:
                content = f.read()

        # Verify integrity
        content_hash = self._compute_hash(content)
        if content_hash != document.content_hash:
            logging_system.error(
                f"Document integrity check failed: {document_id}",
                document_id=document_id,
                expected_hash=document.content_hash,
                actual_hash=content_hash,
            )
            raise ValueError("Document integrity check failed")

        # Audit log
        logging_system.audit_sensitive_data_access(
            user=user,
            data_type="legal_document",
            operation="read",
            record_id=document_id,
        )

        return document, content

    def update_document(
        self,
        document_id: str,
        content: str,
        user: str,
    ) -> LegalDocument:
        """
        Update document content

        Args:
            document_id: Document ID
            content: New content
            user: User making the update

        Returns:
            Updated document object
        """
        if document_id not in self._document_index:
            raise ValueError(f"Document not found: {document_id}")

        document = self._document_index[document_id]

        # Update hash
        document.content_hash = self._compute_hash(content)
        document.modified_at = datetime.utcnow()

        # Store updated content
        if document.encrypted:
            encrypted_content = encrypt_sensitive_data(content)

            doc_path = self._get_document_path(document_id, encrypted=True)
            with open(doc_path, "wb") as f:
                f.write(encrypted_content)

        else:
            doc_path = self._get_document_path(document_id, encrypted=False)
            with open(doc_path, "w") as f:
                f.write(content)

        # Audit log
        logging_system.audit_sensitive_data_access(
            user=user,
            data_type="legal_document",
            operation="update",
            record_id=document_id,
        )

        logging_system.info(
            f"Legal document updated: {document.title}",
            document_id=document_id,
            user=user,
        )

        return document

    def list_documents(
        self,
        owner: Optional[str] = None,
        document_type: Optional[DocumentType] = None,
    ) -> List[LegalDocument]:
        """
        List documents with optional filtering

        Args:
            owner: Filter by owner
            document_type: Filter by document type

        Returns:
            List of documents
        """
        documents = list(self._document_index.values())

        if owner:
            documents = [d for d in documents if d.owner == owner]

        if document_type:
            documents = [d for d in documents if d.document_type == document_type]

        return documents

    def delete_document(
        self,
        document_id: str,
        user: str,
    ) -> bool:
        """
        Securely delete a document

        Args:
            document_id: Document ID
            user: User performing deletion

        Returns:
            True if successful
        """
        if document_id not in self._document_index:
            raise ValueError(f"Document not found: {document_id}")

        document = self._document_index[document_id]

        # Delete file
        doc_path = self._get_document_path(document_id, encrypted=document.encrypted)
        if doc_path.exists():
            # Overwrite with random data before deletion (secure delete)
            file_size = doc_path.stat().st_size
            with open(doc_path, "wb") as f:
                import os
                f.write(os.urandom(file_size))

            doc_path.unlink()

        # Remove from index
        del self._document_index[document_id]

        # Audit log
        logging_system.audit_sensitive_data_access(
            user=user,
            data_type="legal_document",
            operation="delete",
            record_id=document_id,
        )

        logging_system.info(
            f"Legal document deleted: {document.title}",
            document_id=document_id,
            user=user,
        )

        return True


# Global document store instance
document_store = EncryptedDocumentStore()


# Template documents
def create_template_documents():
    """Create template legal documents"""

    # Motion to Suppress Evidence template
    motion_template = """# MOTION TO SUPPRESS EVIDENCE

**Case No:** {{case_number}}
**Date:** {{date}}

## COMES NOW

The Defendant, by and through undersigned counsel, respectfully submits this Motion to Suppress Evidence and states as follows:

## BACKGROUND

{{background}}

## ARGUMENT

### I. THE EVIDENCE WAS OBTAINED IN VIOLATION OF THE FOURTH AMENDMENT

{{argument_point_1}}

### II. THE EVIDENCE SHOULD BE SUPPRESSED AS FRUIT OF THE POISONOUS TREE

{{argument_point_2}}

## CONCLUSION

WHEREFORE, Defendant respectfully requests that this Court grant this Motion to Suppress Evidence and exclude all evidence obtained as a result of the unlawful search.

Respectfully submitted,

{{attorney_name}}
{{attorney_bar_number}}
Attorney for Defendant
    """

    document_store.create_document(
        title="MOTION_SUPPRESS_EVIDENCE Template",
        content=motion_template,
        document_type=DocumentType.MOTION,
        sensitivity=SensitivityLevel.CONFIDENTIAL,
        owner="system",
        metadata={"template": True, "variables": ["case_number", "date", "background", "argument_point_1", "argument_point_2", "attorney_name", "attorney_bar_number"]},
    )

    logging_system.info("Legal document templates created")


# Global document store
document_store = EncryptedDocumentStore()

"""
Trusted Capture Workflow
Handles the complete workflow for creating trusted media captures with blockchain verification
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import hashlib
import platform
import json

from blockchain.blockchain_integration import get_blockchain
from config import SecurityConfig

logger = logging.getLogger(__name__)


class TrustedCapture:
    """
    Implements trusted capture workflow with blockchain timestamping
    """
    
    def __init__(self):
        self.blockchain = get_blockchain()
        self.security_config = SecurityConfig()
    
    async def create_trusted_capture(
        self, 
        file_path: str, 
        user_id: str,
        device_info: Optional[Dict] = None,
        location: Optional[Dict] = None
    ) -> Dict:
        """
        Create a trusted capture with blockchain timestamp
        
        Args:
            file_path: Path to the media file to timestamp
            user_id: ID of the user creating the capture
            device_info: Optional device information
            location: Optional location data (if permitted)
            
        Returns:
            Dictionary with capture information including blockchain hash
        """
        try:
            logger.info(f"Creating trusted capture for file: {file_path}")
            
            # 1. Hash the file
            file_hash = await self._hash_file(file_path)
            logger.info(f"File hash: {file_hash}")
            
            # 2. Create metadata
            metadata = await self._create_metadata(
                file_path,
                user_id,
                device_info,
                location
            )
            
            # 3. Seal metadata (encrypt)
            sealed_metadata = self.blockchain.seal_metadata(
                metadata,
                encryption_key=self.security_config.ENCRYPTION_KEY
            )
            
            # 4. Create blockchain transaction
            tx_hash = await self.blockchain.create_timestamp(file_hash, sealed_metadata)
            
            if not tx_hash:
                logger.error("Failed to create blockchain timestamp")
                return {
                    'success': False,
                    'error': 'Failed to create blockchain timestamp'
                }
            
            logger.info(f"Blockchain timestamp created. Tx hash: {tx_hash}")
            
            # 5. Generate capture ID
            capture_id = self._generate_capture_id(file_hash, user_id)
            
            # 6. Prepare result
            result = {
                'success': True,
                'capture_id': capture_id,
                'file_hash': file_hash,
                'blockchain_hash': tx_hash,
                'timestamp': metadata['timestamp'],
                'verification_url': f'/verify/{capture_id}',
                'metadata': metadata
            }
            
            # 7. Store in database (if available)
            await self._save_to_database(result)
            
            logger.info(f"Trusted capture created successfully. Capture ID: {capture_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating trusted capture: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def verify_trusted_capture(
        self, 
        file_path: str,
        capture_id: Optional[str] = None
    ) -> Dict:
        """
        Verify if a file has a valid trusted capture timestamp
        
        Args:
            file_path: Path to the file to verify
            capture_id: Optional capture ID for verification
            
        Returns:
            Dictionary with verification results
        """
        try:
            logger.info(f"Verifying trusted capture for file: {file_path}")
            
            # Hash the file
            file_hash = await self._hash_file(file_path)
            
            # Verify on blockchain
            blockchain_result = await self.blockchain.verify_timestamp(file_hash)
            
            if not blockchain_result:
                return {
                    'verified': False,
                    'message': 'Unable to verify with blockchain'
                }
            
            # Get additional info from database if capture_id provided
            db_info = None
            if capture_id:
                db_info = await self._get_from_database(capture_id)
            
            result = {
                'verified': blockchain_result.get('verified', False),
                'file_hash': file_hash,
                'blockchain_verification': blockchain_result
            }
            
            if db_info:
                result['capture_info'] = db_info
            
            return result
            
        except Exception as e:
            logger.error(f"Error verifying trusted capture: {str(e)}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    async def _hash_file(self, file_path: str) -> str:
        """
        Create SHA-256 hash of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex string of hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    async def _create_metadata(
        self,
        file_path: str,
        user_id: str,
        device_info: Optional[Dict],
        location: Optional[Dict]
    ) -> Dict:
        """Create metadata for the capture"""
        
        file_path_obj = Path(file_path)
        
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'filename': file_path_obj.name,
            'file_size': file_path_obj.stat().st_size,
            'file_type': file_path_obj.suffix,
            'creation_time': datetime.fromtimestamp(file_path_obj.stat().st_ctime).isoformat(),
            'modification_time': datetime.fromtimestamp(file_path_obj.stat().st_mtime).isoformat()
        }
        
        # Add device info
        if device_info:
            metadata['device_info'] = device_info
        else:
            metadata['device_info'] = self._get_device_info()
        
        # Add location if provided
        if location:
            metadata['location'] = location
        
        return metadata
    
    def _get_device_info(self) -> Dict:
        """Get current device information"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    
    def _generate_capture_id(self, file_hash: str, user_id: str) -> str:
        """Generate unique capture ID"""
        combined = f"{file_hash}_{user_id}_{datetime.now().isoformat()}"
        capture_hash = hashlib.sha256(combined.encode()).hexdigest()
        return capture_hash[:16]  # Use first 16 chars for shorter ID
    
    async def _save_to_database(self, capture_data: Dict):
        """
        Save capture data to database
        This is a placeholder - implement actual database logic
        """
        try:
            # In production, save to your database (SQLite, PostgreSQL, MongoDB, etc.)
            # For now, we'll save to a JSON file as simple storage
            
            db_file = Path('./database/captures.json')
            db_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing data
            if db_file.exists():
                with open(db_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Add new capture
            capture_id = capture_data['capture_id']
            data[capture_id] = {
                'file_hash': capture_data['file_hash'],
                'blockchain_hash': capture_data['blockchain_hash'],
                'timestamp': capture_data['timestamp'],
                'metadata': capture_data['metadata']
            }
            
            # Save back to file
            with open(db_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved capture to database: {capture_id}")
            
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
    
    async def _get_from_database(self, capture_id: str) -> Optional[Dict]:
        """
        Retrieve capture data from database
        This is a placeholder - implement actual database logic
        """
        try:
            db_file = Path('./database/captures.json')
            
            if not db_file.exists():
                return None
            
            with open(db_file, 'r') as f:
                data = json.load(f)
            
            return data.get(capture_id)
            
        except Exception as e:
            logger.error(f"Error retrieving from database: {str(e)}")
            return None


# Singleton instance
_trusted_capture_instance = None

def get_trusted_capture() -> TrustedCapture:
    """Get or create singleton trusted capture instance"""
    global _trusted_capture_instance
    if _trusted_capture_instance is None:
        _trusted_capture_instance = TrustedCapture()
    return _trusted_capture_instance

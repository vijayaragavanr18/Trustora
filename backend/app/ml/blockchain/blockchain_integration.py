"""
Blockchain Integration Module
Handles blockchain interactions for trusted capture and verification
"""
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from web3 import Web3
from eth_account import Account
from config import BlockchainConfig
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class BlockchainIntegration:
    """
    Blockchain integration for timestamping and verification
    Supports Ethereum-compatible networks (Sepolia, Polygon, etc.)
    """
    
    def __init__(self):
        self.config = BlockchainConfig()
        self.w3 = None
        self.contract = None
        self.account = None
        self._initialized = False
        
        # Initialize encryption for metadata
        # In production, use secure key management
        self.cipher_suite = None
    
    def initialize(self):
        """Initialize blockchain connection"""
        try:
            # Connect to blockchain network
            self.w3 = Web3(Web3.HTTPProvider(self.config.PROVIDER_URL))
            
            # Check connection
            if not self.w3.is_connected():
                logger.error("Failed to connect to blockchain network")
                return False
            
            logger.info(f"Connected to blockchain network: {self.config.NETWORK}")
            logger.info(f"Current block number: {self.w3.eth.block_number}")
            
            # Load account from private key (if available)
            if self.config.PRIVATE_KEY and self.config.PRIVATE_KEY != '':
                self.account = Account.from_key(self.config.PRIVATE_KEY)
                logger.info(f"Loaded account: {self.account.address}")
            else:
                logger.warning("No private key configured. Read-only mode.")
            
            # Load smart contract (if available)
            if self.config.CONTRACT_ADDRESS and self.config.CONTRACT_ADDRESS != '':
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.config.CONTRACT_ADDRESS),
                    abi=self.config.CONTRACT_ABI
                )
                logger.info(f"Loaded contract at: {self.config.CONTRACT_ADDRESS}")
            else:
                logger.warning("No contract address configured")
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing blockchain: {str(e)}")
            return False
    
    def create_file_hash(self, file_data: bytes) -> str:
        """
        Create SHA-256 hash of file
        
        Args:
            file_data: File content as bytes
            
        Returns:
            Hex string of hash
        """
        sha256_hash = hashlib.sha256(file_data).hexdigest()
        return sha256_hash
    
    def seal_metadata(self, metadata: Dict, encryption_key: Optional[str] = None) -> bytes:
        """
        Encrypt and seal metadata
        
        Args:
            metadata: Metadata dictionary
            encryption_key: Optional encryption key
            
        Returns:
            Encrypted metadata bytes
        """
        try:
            # Convert metadata to JSON
            metadata_json = json.dumps(metadata, sort_keys=True)
            metadata_bytes = metadata_json.encode('utf-8')
            
            # Encrypt metadata
            if encryption_key:
                key = encryption_key.encode('utf-8')
            else:
                # Use configured key or generate new one
                key = Fernet.generate_key()
            
            cipher_suite = Fernet(key)
            encrypted = cipher_suite.encrypt(metadata_bytes)
            
            return encrypted
            
        except Exception as e:
            logger.error(f"Error sealing metadata: {str(e)}")
            # Return unencrypted as fallback (not recommended for production)
            return metadata_json.encode('utf-8')
    
    async def create_timestamp(self, file_hash: str, sealed_metadata: bytes) -> Optional[str]:
        """
        Create blockchain timestamp for file
        
        Args:
            file_hash: SHA-256 hash of file
            sealed_metadata: Encrypted metadata
            
        Returns:
            Transaction hash or None if failed
        """
        if not self._initialized:
            if not self.initialize():
                logger.error("Blockchain not initialized")
                return None
        
        if not self.contract or not self.account:
            logger.error("Contract or account not available")
            return None
        
        try:
            # Convert file hash to bytes32
            file_hash_bytes = Web3.to_bytes(hexstr=file_hash)
            
            # Build transaction
            transaction = self.contract.functions.createTimestamp(
                file_hash_bytes,
                sealed_metadata
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': self.config.GAS_LIMIT,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=self.account.key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if tx_receipt['status'] == 1:
                logger.info(f"Timestamp created successfully. Tx hash: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error("Transaction failed")
                return None
            
        except Exception as e:
            logger.error(f"Error creating timestamp: {str(e)}")
            return None
    
    async def verify_timestamp(self, file_hash: str) -> Optional[Dict]:
        """
        Verify if file has a blockchain timestamp
        
        Args:
            file_hash: SHA-256 hash of file
            
        Returns:
            Dictionary with verification results or None
        """
        if not self._initialized:
            if not self.initialize():
                return None
        
        if not self.contract:
            logger.error("Contract not available")
            return None
        
        try:
            # Convert file hash to bytes32
            file_hash_bytes = Web3.to_bytes(hexstr=file_hash)
            
            # Call contract verification function
            result = self.contract.functions.verifyTimestamp(file_hash_bytes).call()
            
            # Parse result
            exists, timestamp, metadata = result
            
            if exists:
                return {
                    'verified': True,
                    'timestamp': timestamp,
                    'block_timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                    'metadata': metadata.hex()
                }
            else:
                return {
                    'verified': False,
                    'message': 'No blockchain record found for this file'
                }
            
        except Exception as e:
            logger.error(f"Error verifying timestamp: {str(e)}")
            return None
    
    def get_transaction_info(self, tx_hash: str) -> Optional[Dict]:
        """
        Get information about a blockchain transaction
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction information dictionary
        """
        if not self._initialized:
            if not self.initialize():
                return None
        
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            # Get block info
            block = self.w3.eth.get_block(tx_receipt['blockNumber'])
            
            return {
                'transaction_hash': tx_hash,
                'block_number': tx_receipt['blockNumber'],
                'block_timestamp': datetime.fromtimestamp(block['timestamp']).isoformat(),
                'from_address': tx['from'],
                'to_address': tx['to'],
                'gas_used': tx_receipt['gasUsed'],
                'status': 'success' if tx_receipt['status'] == 1 else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction info: {str(e)}")
            return None
    
    def get_network_info(self) -> Dict:
        """Get current blockchain network information"""
        if not self._initialized:
            if not self.initialize():
                return {}
        
        try:
            return {
                'network': self.config.NETWORK,
                'connected': self.w3.is_connected(),
                'current_block': self.w3.eth.block_number,
                'gas_price': self.w3.eth.gas_price,
                'chain_id': self.w3.eth.chain_id
            }
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {}


# Singleton instance
_blockchain_instance = None

def get_blockchain() -> BlockchainIntegration:
    """Get or create singleton blockchain instance"""
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = BlockchainIntegration()
        _blockchain_instance.initialize()
    return _blockchain_instance

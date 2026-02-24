// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title TrustedCapture
 * @dev Smart contract for timestamping and verifying media captures
 */
contract TrustedCapture {
    
    struct Timestamp {
        bytes32 fileHash;
        uint256 timestamp;
        address creator;
        bytes metadata;
        bool exists;
    }
    
    // Mapping from file hash to timestamp data
    mapping(bytes32 => Timestamp) public timestamps;
    
    // Mapping from creator to their capture hashes
    mapping(address => bytes32[]) public creatorCaptures;
    
    // Events
    event TimestampCreated(
        bytes32 indexed fileHash,
        address indexed creator,
        uint256 timestamp,
        bytes metadata
    );
    
    event TimestampVerified(
        bytes32 indexed fileHash,
        bool verified,
        uint256 timestamp
    );
    
    /**
     * @dev Create a timestamp for a file
     * @param fileHash SHA-256 hash of the file
     * @param metadata Encrypted metadata about the capture
     * @return Timestamp ID
     */
    function createTimestamp(
        bytes32 fileHash,
        bytes memory metadata
    ) public returns (uint256) {
        require(!timestamps[fileHash].exists, "File already timestamped");
        
        timestamps[fileHash] = Timestamp({
            fileHash: fileHash,
            timestamp: block.timestamp,
            creator: msg.sender,
            metadata: metadata,
            exists: true
        });
        
        creatorCaptures[msg.sender].push(fileHash);
        
        emit TimestampCreated(fileHash, msg.sender, block.timestamp, metadata);
        
        return block.timestamp;
    }
    
    /**
     * @dev Verify if a file has been timestamped
     * @param fileHash SHA-256 hash of the file to verify
     * @return exists Whether the timestamp exists
     * @return timestamp When the file was timestamped
     * @return metadata Encrypted metadata
     */
    function verifyTimestamp(bytes32 fileHash) 
        public 
        view 
        returns (
            bool exists,
            uint256 timestamp,
            bytes memory metadata
        ) 
    {
        Timestamp memory ts = timestamps[fileHash];
        return (ts.exists, ts.timestamp, ts.metadata);
    }
    
    /**
     * @dev Get timestamp details
     * @param fileHash SHA-256 hash of the file
     * @return Timestamp struct
     */
    function getTimestamp(bytes32 fileHash) 
        public 
        view 
        returns (Timestamp memory) 
    {
        require(timestamps[fileHash].exists, "Timestamp does not exist");
        return timestamps[fileHash];
    }
    
    /**
     * @dev Get all captures created by an address
     * @param creator Address of the creator
     * @return Array of file hashes
     */
    function getCreatorCaptures(address creator) 
        public 
        view 
        returns (bytes32[] memory) 
    {
        return creatorCaptures[creator];
    }
    
    /**
     * @dev Get the creator of a timestamp
     * @param fileHash SHA-256 hash of the file
     * @return Address of the creator
     */
    function getCreator(bytes32 fileHash) 
        public 
        view 
        returns (address) 
    {
        require(timestamps[fileHash].exists, "Timestamp does not exist");
        return timestamps[fileHash].creator;
    }
    
    /**
     * @dev Check if a file was timestamped before a certain time
     * @param fileHash SHA-256 hash of the file
     * @param beforeTimestamp Unix timestamp to check against
     * @return Whether the file was timestamped before the given time
     */
    function wasTimestampedBefore(
        bytes32 fileHash,
        uint256 beforeTimestamp
    ) 
        public 
        view 
        returns (bool) 
    {
        if (!timestamps[fileHash].exists) {
            return false;
        }
        return timestamps[fileHash].timestamp < beforeTimestamp;
    }
}

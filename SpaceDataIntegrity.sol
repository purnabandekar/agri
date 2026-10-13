
 // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SpaceDataIntegrity {
    struct Dataset {
        string name;
        string hash;
        string owner;
        uint256 timestamp;
        address registeredBy;
        bool exists;
    }

    mapping(uint256 => Dataset) private datasets;
    uint256 public datasetCount;

    event DatasetRegistered(
        uint256 indexed id,
        string name,
        string hash,
        address indexed registeredBy,
        uint256 timestamp
    );

    function registerDataset(
        string memory _name,
        string memory _hash,
        string memory _owner
    ) public returns (uint256) {
        require(bytes(_name).length > 0, "Dataset name required");
        require(bytes(_hash).length == 64, "SHA-256 hash must be 64 hex characters");
        require(bytes(_owner).length > 0, "Owner required");

        uint256 id = ++datasetCount;

        datasets[id] = Dataset({
            name: _name,
            hash: _hash,
            owner: _owner,
            timestamp: block.timestamp,
            registeredBy: msg.sender,
            exists: true
        });

        emit DatasetRegistered(
            id,
            _name,
            _hash,
            msg.sender,
            block.timestamp
        );

        return id;
    }

    function getDataset(uint256 _id)
        public
        view
        returns (
            string memory name,
            string memory hash,
            string memory owner,
            uint256 timestamp,
            address registeredBy
        )
    {
        require(datasets[_id].exists, "Dataset not found");

        Dataset storage d = datasets[_id];

        return (
            d.name,
            d.hash,
            d.owner,
            d.timestamp,
            d.registeredBy
        );
    }

    function verifyDataset(uint256 _id, string memory _hash)
        public
        view
        returns (bool)
    {
        require(datasets[_id].exists, "Dataset not found");

        return keccak256(bytes(datasets[_id].hash))
            == keccak256(bytes(_hash));
    }
}

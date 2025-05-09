// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Jobs {
    // Struct to represent a Job, matching the SQLite table
    struct Job {
        uint256 id;              // Auto-incrementing ID
        string title;           // Job title, non-empty
        string description;     // Job description, non-empty
        uint256 created_at;     // Timestamp of creation
        uint256 threshold;      // Threshold as a percentage (scaled by 100 for precision)
        uint256 max_candidates; // Maximum number of candidates
        string summary;         // Optional summary
    }

    // Array to store all jobs
    Job[] public jobs;

    // Mapping to track job existence and index for quick lookup
    mapping(uint256 => uint256) private jobIdToIndex;

    // Counter for auto-incrementing job IDs
    uint256 private nextJobId = 1;

    // Owner of the contract
    address public owner;

    // Event emitted when a job is added
    event JobAdded(uint256 indexed id, string title, uint256 created_at);

    // Event emitted when a job summary is updated
    event JobSummaryUpdated(uint256 indexed id, string summary);

    // Modifier to restrict functions to the owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    // Constructor to set the contract owner
    constructor() {
        owner = msg.sender;
    }

    // Function to insert a new job
    function addJob(
        string calldata _title,
        string calldata _description,
        uint256 _threshold,
        uint256 _max_candidates,
        string calldata _summary
    ) external onlyOwner {
        // Validate inputs
        require(bytes(_title).length > 0, "Title cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(_threshold <= 10000, "Threshold must be <= 100.00");
        require(_max_candidates > 0, "Max candidates must be positive");

        // Create new job
        Job memory newJob = Job({
            id: nextJobId,
            title: _title,
            description: _description,
            created_at: block.timestamp,
            threshold: _threshold,
            max_candidates: _max_candidates,
            summary: _summary
        });

        // Add job to array and update mapping
        jobs.push(newJob);
        jobIdToIndex[nextJobId] = jobs.length - 1;

        // Emit event
        emit JobAdded(nextJobId, _title, block.timestamp);

        // Increment ID for next job
        nextJobId++;
    }

    // Function to update the summary of an existing job
    function updateJobSummary(uint256 _id, string calldata _summary) external onlyOwner {
        require(_id > 0 && _id < nextJobId, "Invalid job ID");
        uint256 index = jobIdToIndex[_id];
        require(index < jobs.length, "Job does not exist");

        // Update the summary
        jobs[index].summary = _summary;

        // Emit event
        emit JobSummaryUpdated(_id, _summary);
    }

    // Function to get a single job by ID
    function getJob(uint256 _id) external view returns (Job memory) {
        require(_id > 0 && _id < nextJobId, "Invalid job ID");
        uint256 index = jobIdToIndex[_id];
        require(index < jobs.length, "Job does not exist");
        return jobs[index];
    }

    // Function to get all jobs
    function getAllJobs() external view returns (Job[] memory) {
        return jobs;
    }

    // Function to get the total number of jobs
    function getJobCount() external view returns (uint256) {
        return jobs.length;
    }
}
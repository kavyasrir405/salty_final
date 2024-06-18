import React, { useState } from 'react';
import axios from 'axios';

export default function IssueStatus({ issueName ,pid,onissueTypeChange}) {
  const [selectedStatus, setSelectedStatus] = useState(issueName.status);
console.log("issuestaus",issueName)
  const handleStatusChange = async (event) => {
    const newStatus = event.target.value;
    setSelectedStatus(newStatus);
    onissueTypeChange(true)
   
    try {
      await axios.post('http://localhost:8000/djapp/update_issueStatus/', { issue:issueName.IssueName ,status: newStatus,projectId:pid});    } catch (error) {
      console.error('Error updating issue status:', error);
    }
  };

  return (
    <div>
      <select id="status" value={selectedStatus} onChange={handleStatusChange}>
        <option value="To-Do">To Do</option>
        <option value="In-Progress">In Progress</option>
        <option value="Done">Done</option>
      </select>
    </div>
  );
}



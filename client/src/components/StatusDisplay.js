// src/components/StatusDisplay.js
import React from 'react';

const StatusDisplay = ({ status, downloadLink, onDownload }) => {
  return (
    <div>
      <p>Status: {status}</p>
      {status === 'completed' && (
        <button onClick={onDownload}>
          Download Audio
        </button>
      )}
    </div>
  );
};

export default StatusDisplay;

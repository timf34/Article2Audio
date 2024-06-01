// src/components/StatusDisplay.js
import React from 'react';

const StatusDisplay = ({ status, downloadLink }) => {
  return (
    <div>
      <p>Status: {status}</p>
      {downloadLink && (
        <a href={downloadLink} download>
          Download Audio
        </a>
      )}
    </div>
  );
};

export default StatusDisplay;

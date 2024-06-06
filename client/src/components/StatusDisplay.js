import React from 'react';

const StatusDisplay = ({ status, estimatedTime, downloadLink, onDownload }) => {
  return (
    <div>
      <p>Status: {status}</p>
      {status === 'Processing...' && <p>Estimated time: {estimatedTime} seconds</p>}
      {status === 'completed' && (
        <button onClick={onDownload}>
          Download Audio
        </button>
      )}
    </div>
  );
};

export default StatusDisplay;

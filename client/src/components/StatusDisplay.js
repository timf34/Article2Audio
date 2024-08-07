import React, { useState, useEffect } from 'react';

const StatusDisplay = ({ status, estimatedTime,}) => {
  const [displayTime, setDisplayTime] = useState(estimatedTime);

  useEffect(() => {
    if ((status === 'Creating audio file...') && estimatedTime > 0) {
      setDisplayTime(estimatedTime);
      const countdown = setInterval(() => {
        setDisplayTime((prevTime) => {
          if (prevTime > 1) {
            return prevTime - 1;
          } else {
            clearInterval(countdown);
            return 0;
          }
        });
      }, 1000);

      return () => clearInterval(countdown);
    }
  }, [status, estimatedTime]);

  return (
    <div>
      <p>Status: {status}</p>
      {(status === 'Creating audio file...') && (
        <p>
          Estimated time: {displayTime > 0 ? `${displayTime} seconds` : 'any minute now!'}
        </p>
      )}
      {status === 'completed' && (
        <p>
          Audio ready, refresh the page!
        </p>
      )}
    </div>
  );
};

export default StatusDisplay;

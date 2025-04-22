import React, { useState, useEffect } from 'react';
import './Dashboard.css';

function Dashboard() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="dashboard">
      <div className="time-widget">
        <div className="time">{time.toLocaleTimeString()}</div>
        <div className="date">{time.toLocaleDateString()}</div>
      </div>
    </div>
  );
}

export default Dashboard; 
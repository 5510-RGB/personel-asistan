import React from 'react';
import './Dashboard.css';

function Dashboard() {
  const [currentTime, setCurrentTime] = React.useState(new Date());
  const [reminders, setReminders] = React.useState([
    { id: 1, title: 'Toplantı', time: '14:00' },
    { id: 2, title: 'Doktor Randevusu', time: '16:30' }
  ]);

  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="dashboard">
      <div className="time-widget">
        <div className="time">{currentTime.toLocaleTimeString()}</div>
        <div className="date">{currentTime.toLocaleDateString()}</div>
      </div>
      
      <div className="reminders-widget">
        <h3>Hatırlatıcılar</h3>
        <div className="reminders-list">
          {reminders.map(reminder => (
            <div key={reminder.id} className="reminder-item">
              <span>{reminder.title}</span>
              <span>{reminder.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 
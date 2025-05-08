import React, { useState } from 'react';
import './RegistrationWidget.css';

const RegistrationWidget = () => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleRegister = async () => {
    if (!name) {
      setMessage("Name is required!");
      return;
    }

    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:5001/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`Face registered for ${name}`);
      } else {
        setMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      setMessage('Error occurred while registering face.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="widget-container">
      <h2>Register Face</h2>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter name"
      />
      <button onClick={handleRegister} disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default RegistrationWidget;

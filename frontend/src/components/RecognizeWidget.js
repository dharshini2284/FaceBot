import React, { useState } from 'react';
import './RecognizeWidget.css';

const RecognizeWidget = () => {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRecognize = async () => {
    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:5001/api/recognize');
      const data = await response.json();
      
      if (response.ok) {
        setMessage('Recognition started.');
      } else {
        setMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      setMessage('Error occurred while starting face recognition.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="widget-container">
      <h2>Recognize Face</h2>
      <button onClick={handleRecognize} disabled={loading}>
        {loading ? 'Recognizing...' : 'Recognize Face'}
      </button>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default RecognizeWidget;

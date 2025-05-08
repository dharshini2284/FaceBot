import React, { useState, useEffect } from 'react';
import axios from 'axios';  // Import Axios
import './ChatWidget.css';

const ChatWidget = () => {
  const [message, setMessage] = useState('');  
  const [response, setResponse] = useState('');  
  const [loading, setLoading] = useState(false); 
  const [error, setError] = useState(null);      

  const handleSendMessage = async () => {
    if (message.trim()) {
      setLoading(true);  
      setResponse('');   
      setError(null);    

      try {
        // Send the message to the backend via HTTP POST request
        const res = await axios.post('http://localhost:8765/api/ask', {
          query: message
        });

        // Set the response from the server
        setResponse(res.data.answer);
      } catch (err) {
        // Handle error if HTTP request fails
        setError('Error occurred while sending the request. Please try again.');
        console.error('Error:', err);
      } finally {
        setLoading(false);  
      }
    }
  };

  return (
    <div className="chat-widget-container">
      <h2>Chat with RAG Engine</h2>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleSendMessage} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>
      {error && <p className="error-message">{error}</p>}  
      {response && <p className="response">{response}</p>}  
    </div>
  );
};

export default ChatWidget;

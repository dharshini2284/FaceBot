import React from 'react';
import RegistrationWidget from './components/RegistrationWidget';
import RecognizeWidget from './components/RecognizeWidget';
import ChatWidget from './components/ChatWidget';
import './App.css';

const App = () => {
  return (
    <div className="app-container">
      <h1>FaceBot</h1>
      <div className="widgets-container">
        <RegistrationWidget />
        <RecognizeWidget />
        <ChatWidget />
      </div>
    </div>
  );
};

export default App;

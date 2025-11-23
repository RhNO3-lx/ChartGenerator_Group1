import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Workbench from './components/Workbench';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Workbench />} />
      </Routes>
    </Router>
  );
}

export default App;

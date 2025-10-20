import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import GerarCalculo from './pages/GerarCalculo';
import Historico from './pages/Historico';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 py-8">
        <Navbar />
        
        <Routes>
          <Route path="/" element={<GerarCalculo />} />
          <Route path="/historico" element={<Historico />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

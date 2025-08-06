import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import PDFAnalyzer from './pages/PDFAnalyzer';
import LegalQuery from './pages/LegalQuery';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pdf-analyzer" element={<PDFAnalyzer />} />
          <Route path="/legal-query" element={<LegalQuery />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ProductDetails from './components/ProductDetails';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/details/:productId" element={<ProductDetails />} />
                {/* Add more routes as needed */}
            </Routes>
        </Router>
    );
}

export default App;

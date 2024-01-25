"use client"
import React, { useState } from 'react';
import axios from 'axios';

const FlaskPage = () => {
    const [message, setMessage] = useState('');

    const fetchHelloWorld = async () => {
        try {
            const response = await axios.get('/api/hello');
            setMessage(response.data.message);
        } catch (error) {
            console.error('Error:', error);
            setMessage('Failed to fetch message');
        }
    };

    return (
        <div>
            <h1>Flask Example</h1>
            <button onClick={fetchHelloWorld}>Fetch Message from Flask</button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default FlaskPage;

"use client"
import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { motion } from 'framer-motion';

const HeroSection = () => {
    return (
        <Box textAlign="center" pt={8} pb={6}>
            <motion.div
                initial={{ y: -250, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2, type: 'spring', stiffness: 100 }}
            >
                <Typography variant="h3" component="h1" gutterBottom>
                    Welcome to Base App
                </Typography>
                <Typography variant="h5" color="text.secondary" paragraph>
                    A starter template for Next.js apps with Material UI, Framer Motion, and more.
                </Typography>
                <Button variant="contained" size="large">
                    Get Started
                </Button>
            </motion.div>
        </Box>
    );
};

export default HeroSection;

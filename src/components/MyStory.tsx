"use client"
import React from 'react';
import { Box, Typography } from '@mui/material';
import { motion } from 'framer-motion';

const MyStory = () => {
    return (
        <Box sx={{ my: 4 }}>
            <motion.div
                initial={{ opacity: 0, x: -100 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Typography variant="h4" gutterBottom>
                    My Story
                </Typography>
                <Typography variant="body1">
                    As I was learning front-end development, I discovered that MUI offers a robust set of components for building UIs efficiently. Coupled with Next.js and its new app router, I found a powerful stack for modern web applications. However, the lack of comprehensive examples combining these technologies motivated me to create this template. It's designed to be highly commented and demonstrative, making it an ideal starting point for both learning and development.
                </Typography>
            </motion.div>
        </Box>
    );
};

export default MyStory;

"use client"
import React from 'react';
import { Box, Typography, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { motion } from 'framer-motion';

const features = [
    'MUI components for rapid UI development',
    'Highly commented code for educational purposes',
    'Integration with framer-motion for that extra flair',
    'Next.js app router usage examples',
];

const Features = () => {
    return (
        <Box sx={{ my: 4 }}>
            <motion.div
                initial={{ opacity: 0, y: 100 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Typography variant="h4" gutterBottom>
                    Features
                </Typography>
                <List>
                    {features.map((feature, index) => (
                        <ListItem key={index}>
                            <ListItemIcon>
                                <CheckCircleIcon color="primary" />
                            </ListItemIcon>
                            <ListItemText primary={feature} />
                        </ListItem>
                    ))}
                </List>
            </motion.div>
        </Box>
    );
};

export default Features;

"use client"
import { Box, Typography, Button, Container } from '@mui/material';
import { motion } from 'framer-motion';

const HeroSection = () => (
    <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
    >
        <Box sx={{
            textAlign: 'center',
            pt: 8, // Increase top padding
            pb: 8, // Increase bottom padding
            minHeight: '100vh', // Set minimum height to 100% of the viewport height
            backgroundImage: 'url(/hero-bg.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center', // Ensure the background image is centered
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center', // Vertically center the content
        }}>
            <Container>
            <Typography variant="h1">Welcome to Template</Typography>
            <Typography variant="h4" sx={{ my: 2 }}>Discover Our Amazing Product</Typography>
            <Button variant="contained" color="primary" size="large">Get Started</Button>
            </Container>
            </Box>
    </motion.div>
);

export default HeroSection;

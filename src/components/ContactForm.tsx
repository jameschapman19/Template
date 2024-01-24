"use client"
import { motion, useAnimation } from 'framer-motion';
import { useEffect, useRef } from 'react';
import { useInView } from 'framer-motion';
import { Box, TextField, Container, Button, Typography } from '@mui/material';

const variants = {
    visible: i => ({
        opacity: 1,
        x: 0,
        transition: {
            delay: i * 0.2
        }
    }),
    hidden: { opacity: 0, x: -50 }
};

const ContactForm = () => {
    const controls = useAnimation();
    const ref = useRef(null);
    const isInView = useInView(ref,{ once: true, amount:0.5 });

    useEffect(() => {
        if (isInView) {
            controls.start('visible');
        }
    }, [controls, isInView]);

    return (
        <Box ref={ref} sx={{ p: 4 ,textAlign: 'center',
            minHeight: '100vh', // Set minimum height to 100% of the viewport height
            backgroundImage: 'url(/hero-bg.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center', // Ensure the background image is centered
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center', // Vertically center the content}>
        }}>
            <Container>
            <motion.div initial="hidden" animate={controls} variants={variants}>
            <Typography variant="h4" gutterBottom>Contact Us</Typography>
            <Typography variant="subtitle1" sx={{ mb: 4 }}>
                We're here to help
            </Typography>
            </motion.div>
            <form noValidate autoComplete="off">
                {['Name', 'Email', 'Message'].map((label, index) => (
                    <motion.div
                        key={label}
                        custom={index}
                        initial="hidden"
                        animate={controls}
                        variants={variants}
                    >
                        <TextField
                            label={label}
                            fullWidth
                            sx={{ my: 2 }}
                            multiline={label === 'Message'}
                            rows={label === 'Message' ? 4 : 1}
                        />
                    </motion.div>
                ))}
                <motion.div initial="hidden" animate={controls} variants={variants} custom={3}>
                    <Button variant="contained" color="primary">Submit</Button>
                </motion.div>
            </form>
            </Container>
        </Box>
    );
};

export default ContactForm;

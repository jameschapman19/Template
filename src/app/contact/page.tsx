"use client"
import React, { useEffect } from 'react';
import { Container, Typography, Box, TextField, Button, Grid } from '@mui/material';
import { motion, useAnimation } from 'framer-motion';

const Contact = () => {
    const controls = useAnimation();

    useEffect(() => {
        controls.start(i => ({
            opacity: 1,
            translateY: 0,
            transition: { delay: i * 0.2 }
        }));
    }, [controls]);

    const fieldVariants = {
        hidden: { opacity: 0, translateY: 50 }
    };

    return (
        <Container sx={{ py: 4 }}>
            <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                    <Box display="flex" flexDirection="column" justifyContent="center" height="100%">
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8 }}
                        >
                        <Typography variant="h2" component="h1" sx={{
                            fontWeight: 'bold',
                        }} gutterBottom>
                            Contact Us
                        </Typography>
                        <Typography paragraph>
                            Have questions or need support? Our team is here to help.
                        </Typography>
                        </motion.div>
                    </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Box component="form" noValidate autoComplete="off">
                        {['Name', 'Email', 'Message'].map((label, index) => (
                            <motion.div
                                key={label}
                                custom={index}
                                initial="hidden"
                                animate={controls}
                                variants={fieldVariants}
                            >
                                <TextField
                                    label={label}
                                    fullWidth
                                    multiline={label === 'Message'}
                                    rows={label === 'Message' ? 4 : 1}
                                    sx={{ my: 2 }}
                                />
                            </motion.div>
                        ))}
                        <motion.div custom={3} initial="hidden" animate={controls} variants={fieldVariants}>
                            <Button variant="contained" color="primary">Send Message</Button>
                        </motion.div>
                    </Box>
                </Grid>
            </Grid>
        </Container>
    );
};

export default Contact;

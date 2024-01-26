"use client"
import React from 'react';
import { Container, Typography, Box, Grid, Link } from '@mui/material';
import { motion } from 'framer-motion';
import Image from 'next/image';
import socials from '@/content/socials.json';
import GitHubIcon from "@mui/icons-material/GitHub";
import LinkedInIcon from "@mui/icons-material/LinkedIn";
import TwitterIcon from "@mui/icons-material/Twitter";
import InstagramIcon from "@mui/icons-material/Instagram"; // Import the JSON file for social links


const About = () => {

    const getIcon = (name: string) => {
        switch (name) {
            case 'GitHub':
                return <GitHubIcon />;
            case 'LinkedIn':
                return <LinkedInIcon />;
            case 'Twitter':
                return <TwitterIcon />;
            case 'Instagram':
                return <InstagramIcon />;
            default:
                return null;
        }
    };

    return (
        <Container>
            <Box sx={{ textAlign: 'center', p: 4, minHeight: '100vh'}}>
                <motion.div
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.6 }}
                >
                    <Typography variant="h2" gutterBottom sx={{
                        fontWeight: 'bold',
                    }}>
                        About James Chapman
                    </Typography>
                    <Typography variant="h6" sx={{ my: 2 }}>
                        A Journey from Scientific Python to Web Developer
                    </Typography>
                </motion.div>
                <Grid container spacing={4} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <motion.div
                            initial={{ x: -50, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ duration: 0.6 }}
                        >
                            <Typography>
                                Coming from a PhD in Machine Learning with a solid background in Python, I aspired to broaden my skills into web development. This template is a culmination of my self-taught journey in creating cool and functional web products.
                            </Typography>
                            <Box sx={{ mt: 2 }}>
                                {socials.map((social, index) => (
                                    <Link key={index} href={social.url} target="_blank" sx={{ mx: 1 }}>
                                        {getIcon(social.name)}
                                    </Link>
                                ))}
                            </Box>
                        </motion.div>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <motion.div
                            initial={{ x: 50, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ duration: 0.6 }}
                        >
                            {/* Placeholder image of James Chapman */}
                            <Image
                                src="/Me.jpg"
                                alt="James Chapman"
                                width={500}
                                height={500}
                                layout="responsive"
                                objectFit="cover"
                                quality={100}

                            />
                        </motion.div>
                    </Grid>
                </Grid>
            </Box>
        </Container>
    );
};

export default About;

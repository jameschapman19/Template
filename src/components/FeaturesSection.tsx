"use client";
import { Grid, Card, CardContent, Container, Typography, Box } from '@mui/material';
import { motion, useAnimation } from 'framer-motion';
import { useEffect, useRef } from 'react';
import { useInView } from 'framer-motion';
import theme from '@/components/ThemeRegistry/theme';

const featuresSection = [
    { title: 'Seamless Integration', description: 'Combine the best of both worlds with Next.js and Flask working together in harmony.' },
    { title: 'TypeScript Ready', description: 'Leverage the power of strong typing to build more reliable and maintainable apps.' },
    { title: 'Material UI Design', description: 'Speed up your UI development with pre-built Material UI components that are customizable and responsive.' },
];

const FeaturesSection = () => {
    const controls = useAnimation();
    const ref = useRef(null);
    const isInView = useInView(ref,{  amount:0.5 });

    useEffect(() => {
        if (isInView) {
            controls.start('visible');
        }
    }, [controls, isInView]);

    const variants = {
        visible: { opacity: 1, y: 0, transition: { duration: 0.6, delay: 0.2 } },
        hidden: { opacity: 0, y: 50 },
    };

    return (
        <Box ref={ref}  sx={{
            py: 8, // Vertical padding
            textAlign: 'center',
            backgroundColor: theme.palette.primary.main, // Use primary color from theme
            minHeight: '100vh', // Set minimum height to 100% of the viewport height
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center', // Vertically center the content
        }}>
            <Container>
            <motion.div initial="hidden" animate={controls} variants={variants}>
                <Typography variant="h2" gutterBottom sx={{ color: theme.palette.secondary.contrastText, fontWeight: 'bold' }}>Our Top Features</Typography>
                <Typography variant="h5" sx={{ mb: 4, color: theme.palette.secondary.contrastText }}>
                    Discover what makes us stand out
                </Typography>
            </motion.div>
            <Grid container spacing={2}>
                {featuresSection.map((feature, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                        <motion.div
                            initial="hidden"
                            animate={controls}
                            variants={variants}
                            whileHover={{ scale: 1.05 }}
                        >
                        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: "white" }}>
                            <CardContent sx={{ flexGrow: 1 }}>
                                <Typography gutterBottom variant="h5" component="div" sx={{fontWeight: 'bold' }} >
                                    {feature.title}
                                </Typography>
                                <Typography variant="body2">
                                    {feature.description}
                                </Typography>
                            </CardContent>
                        </Card>
                        </motion.div>
                    </Grid>
                ))}
            </Grid>
            </Container>
        </Box>
    );
};

export default FeaturesSection;

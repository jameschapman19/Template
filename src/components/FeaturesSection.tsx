"use client";
import { Grid, Card, CardContent, Container, Typography, Box } from '@mui/material';
import { motion, useAnimation } from 'framer-motion';
import { useEffect, useRef } from 'react';
import { useInView } from 'framer-motion';
import theme from '@/theme';

const featuresSection = [
    { title: 'Feature 1', description: 'Description for feature 1' },
    { title: 'Feature 2', description: 'Description for feature 2' },
    { title: 'Feature 3', description: 'Description for feature 3' },
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
            p: 4,
            textAlign: 'center',
            minHeight: '100vh', // Set minimum height to 100% of the viewport height
            background: theme.palette.secondary.light,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center', // Vertically center the content
        }}>
            <Container>
            <motion.div initial="hidden" animate={controls} variants={variants}>
                <Typography variant="h4" gutterBottom sx={{  color: "white" }}>Our Top Features</Typography>
                <Typography variant="subtitle1" sx={{ mb: 4, color: "white" }}>
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
                            <Card>
                                <CardContent>
                                    <Typography variant="h5">{feature.title}</Typography>
                                    <Typography>{feature.description}</Typography>
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

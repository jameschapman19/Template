"use client"
import React from 'react';
import { Typography, Box, Container, Grid, Card, CardMedia, CardContent, CardActions, Button, Link } from '@mui/material';
import { motion } from 'framer-motion';

// Example data for the gallery
const galleryItems = [
    {
        id: 1,
        title: "Website 1",
        description: "Description of Website 1.",
        imageUrl: "https://source.unsplash.com/random?website1",
        link: "https://website1.com"
    },
    {
        id: 2,
        title: "Website 2",
        description: "Description of Website 2.",
        imageUrl: "https://source.unsplash.com/random?website2",
        link: "https://website2.com"
    },
    // ... more items
];

export default function Gallery() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
        >
                <Box sx={{ bgcolor: 'background.paper', pt: 8, pb: 6 }}>
                    <Container maxWidth="sm">
                        <Typography component="h1" variant="h2" align="center" color="text.primary"
                            fontWeight='bold' gutterBottom>
                            Helpful Websites
                        </Typography>
                        <Typography variant="h5" align="center" color="text.secondary" paragraph>
                            A collection of websites that inspired and guided the creation of this template.
                        </Typography>
                    </Container>
                </Box>
                <Container sx={{ py: 8 }} maxWidth="md">
                    <Grid container spacing={4}>
                        {galleryItems.map((item) => (
                            <Grid item key={item.id} xs={12} sm={6} md={4}>
                                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                    <CardMedia component="img" image={item.imageUrl} alt={item.title} />
                                    <CardContent sx={{ flexGrow: 1 }}>
                                        <Typography gutterBottom variant="h5" component="h2">
                                            {item.title}
                                        </Typography>
                                        <Typography>
                                            {item.description}
                                        </Typography>
                                    </CardContent>
                                    <CardActions>
                                        <Button size="small" component={Link} href={item.link} target="_blank">
                                            Visit
                                        </Button>
                                    </CardActions>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                </Container>
        </motion.div>
    );
}

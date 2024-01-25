"use client"
import React, { useState } from 'react';
import { Container, Card, Box, Grid, Typography, Paper, TextField, Button, CardContent, CardActionArea, CardMedia} from '@mui/material';
import { motion } from 'framer-motion';
import FileUpload from '@/components/FileUpload';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DescriptionIcon from '@mui/icons-material/Description';




const Product = () => {
    const [query, setQuery] = useState('');
    const [files, setFiles] = useState([]);

    const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleQuerySubmit = () => {
        console.log(query);
    };

    const handleFileUpload = (newFiles) => {
        setFiles([...files, ...newFiles]);
    };

    const getFileIcon = (fileType) => {
        switch (fileType) {
            case 'application/pdf':
                return <PictureAsPdfIcon />;
            case 'application/msword':
            case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return <DescriptionIcon />;
            default:
                return <DescriptionIcon />;
        }
    };

    return (
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
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                <Typography variant="h3" gutterBottom sx={{ mt: 4 }}>
                    Product Demo
                </Typography>
                <Typography paragraph>
                    Drag and drop your PDF or Word files here to see our product in action.
                </Typography>
                <FileUpload onFileUpload={handleFileUpload} />
                    <Grid container spacing={2} sx={{ mt: 2 }}>
                        {files.map((file, index) => (
                            <Grid item key={index} xs={6} sm={4} md={3} lg={2}>
                                <Card>
                                    <CardActionArea>
                                        <CardMedia>
                                            {getFileIcon(file.type)}
                                        </CardMedia>
                                        <CardContent>
                                            <Typography noWrap>
                                                {file.name}
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                <Paper elevation={3} sx={{ p: 2, mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Query Your Documents
                    </Typography>
                    <TextField
                        label="Enter your query"
                        variant="outlined"
                        fullWidth
                        value={query}
                        onChange={handleQueryChange}
                        sx={{ mb: 2 }}
                    />
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleQuerySubmit}
                        fullWidth
                    >
                        Submit Query
                    </Button>
                </Paper>
                </motion.div>
                </Container>
            </Box>
    );
};

export default Product;

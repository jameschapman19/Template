"use client"
import React, { useState } from 'react';
import { Container, Typography, Paper, TextField, Button, Grid, Card, CardContent, CardActionArea, CardMedia } from '@mui/material';
import { motion } from 'framer-motion';
import FileUpload from '@/components/FileUpload';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DescriptionIcon from '@mui/icons-material/Description';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

const Product = () => {
    const [query, setQuery] = useState('');
    const [files, setFiles] = useState<File[]>([]);
    const [response, setResponse] = useState(''); // State to store the response from the server

    const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleQuerySubmit = async () => {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        formData.append('query', query);

        try {
            const response = await axios.post('/api/process', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setResponse(JSON.stringify(response.data)); // Set the response state
        } catch (error) {
            console.error('Error submitting files and query:', error);
            setResponse('Failed to fetch response');
        }
    };

    const handleFileUpload = (newFiles: File[]) => {
        setFiles([...files, ...newFiles]);
    };

    const getFileIcon = (fileType: any) => {
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

    const handleRemoveFile = (index: number) => {
        setFiles(files.filter((_, fileIndex) => fileIndex !== index));
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
        >
            <Container maxWidth="md">
                <Typography variant="h2" gutterBottom sx={{ mt: 4,textAlign: 'center',
                    fontWeight: 'bold',
                }}>
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
                                <Button
                                    color="error"
                                    startIcon={<DeleteIcon />}
                                    onClick={() => handleRemoveFile(index)}
                                >
                                    Remove
                                </Button>
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
                {/* Display the response from the server */}
                <Paper elevation={3} sx={{ p: 2, mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Server Response
                    </Typography>
                    <Typography>
                        {response}
                    </Typography>
                </Paper>
            </Container>
        </motion.div>
    );
};

export default Product;
"use client"
import React, { useState } from 'react';
import { Container,Box, Typography, Paper, TextField, Button, Grid, Card, CardContent, CardActionArea, CardMedia } from '@mui/material';
import { motion } from 'framer-motion';
import FileUpload from '@/components/FileUpload';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DescriptionIcon from '@mui/icons-material/Description';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';
import CircularProgress from '@mui/material/CircularProgress';

const LoadingAnimation = () => (
    <Box sx={{ textAlign: 'center', mt: 4 }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
            Processing your request...
        </Typography>
    </Box>
);

// @ts-ignore
const ResultDisplay = ({ result }) => (
    <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ marginTop: '20px', textAlign: 'center' }}
    >
        <Typography variant="h4" style={{ fontWeight: 'bold' }}>
            Result:
        </Typography>
        <Typography variant="h5" style={{ color: '#4caf50', marginTop: '10px' }}>
            {result}
        </Typography>
    </motion.div>
);

const Product = () => {
    const [query, setQuery] = useState('');
    const [files, setFiles] = useState<File[]>([]);
    const [response, setResponse] = useState(''); // State to store the response from the server
    const [isLoading, setIsLoading] = useState(false);
    const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleQuerySubmit = async () => {
        setIsLoading(true); // Start loading
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        formData.append('query', query);

        try {
            const response = await axios.post('/api/process', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            // Set only the 'result' part of the response
            setResponse(response.data.result);
        } catch (error) {
            console.error('Error submitting files and query:', error);
            setResponse('Failed to fetch response');
        }
        setIsLoading(false); // Stop loading once the API call is complete
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
                {isLoading ? (
                    <LoadingAnimation />
                ) : (
                    response && <ResultDisplay result={response} />
                )}
            </Container>
        </motion.div>
    );
};

export default Product;
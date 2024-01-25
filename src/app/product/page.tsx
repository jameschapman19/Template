"use client"
import React, { useState } from 'react';
import { Container, Typography, Paper, TextField, Button, Grid, Card, CardContent, CardActionArea, CardMedia } from '@mui/material';
import { motion } from 'framer-motion';
import FileUpload from '@/components/FileUpload';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DescriptionIcon from '@mui/icons-material/Description';

const Product = () => {
    const [query, setQuery] = useState('');
    const [files, setFiles] = useState<File[]>([]);

    const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);
    };

    const handleQuerySubmit = () => {
        console.log(query);
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

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <Container maxWidth="md">
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
            </Container>
        </motion.div>
    );
};

export default Product;
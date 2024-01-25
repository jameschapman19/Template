// components/FileUpload.tsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Typography, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import axios from '../utils/axiosConfig'; // Import the Axios instance

const FileUpload = () => {
    const onDrop = useCallback(async (acceptedFiles) => {
        const formData = new FormData();
        acceptedFiles.forEach(file => formData.append('files', file));

        try {
            const response = await axios.post('/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log(response.data); // Handle the response as needed
        } catch (error) {
            if (axios.isAxiosError(error)) {
                console.error('Error uploading file: ', error.response?.data);
            } else {
                console.error('Unexpected error: ', error);
            }
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

    return (
        <Paper {...getRootProps()} elevation={3} sx={{ border: '2px dashed grey', p: 4, textAlign: 'center', backgroundColor: '#f0f0f0', cursor: 'pointer' }}>
            <input {...getInputProps()} />
            <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: isDragActive ? 1.1 : 1 }}
                transition={{ duration: 0.2 }}
            >
                <Typography variant="h6">
                    {isDragActive ? 'Drop the files here ...' : 'Drag and drop some files here, or click to select files'}
                </Typography>
            </motion.div>
        </Paper>
    );
};

export default FileUpload;

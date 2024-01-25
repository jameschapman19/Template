// components/FileUpload.tsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Typography, Paper } from '@mui/material';
import { motion } from 'framer-motion';

interface FileUploadProps {
    onFileUpload: (files: File[]) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        onFileUpload(acceptedFiles);
    }, [onFileUpload]);

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

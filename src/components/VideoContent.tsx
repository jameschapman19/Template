import React, { useRef, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

const VideoContent = ({ src, alt, title, description }) => {
    const videoRef = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        videoRef.current.play();
                    } else {
                        videoRef.current.pause();
                    }
                });
            },
            {
                threshold: 0.5 // Trigger when 50% of the video is visible
            }
        );

        if (videoRef.current) {
            observer.observe(videoRef.current);
        }

        return () => {
            if (videoRef.current) {
                observer.unobserve(videoRef.current);
            }
        };
    }, []);

    return (
        <Box sx={{
            textAlign: 'center',
            pt: 8, // Increase top padding
            pb: 8, // Increase bottom padding
            minHeight: '100vh', // Set minimum height to 100% of the viewport height
            position: 'relative',
            overflow: 'hidden' }}>
            <video
                ref={videoRef}
                src={src}
                alt={alt}
                muted
                loop
                style={{ width: '100%', height: 'auto' }}
            />
            <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'white', textAlign: 'center' }}>
                <Typography variant="h1">{title}</Typography>
                <Typography variant="h2">{description}</Typography>
            </Box>
        </Box>
    );
};

export default VideoContent;

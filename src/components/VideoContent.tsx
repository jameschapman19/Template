import React, { useRef, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

// @ts-ignore
const VideoContent = ({ src, title, description }) => {
    const videoRef = useRef<HTMLVideoElement | null>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting && videoRef.current) {
                        videoRef.current.play();
                    } else if (videoRef.current) {
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
                // eslint-disable-next-line react-hooks/exhaustive-deps
                observer.unobserve(videoRef.current);
            }
        };
    }, []);

    return (
        <Box sx={{
            position: 'relative',
            overflow: 'hidden',
            textAlign: 'center',
            '&:before': { // Dark overlay for better text visibility
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                backgroundColor: 'rgba(0, 0, 0, 0.5)', // Adjust the color and opacity as needed
            }
        }}>
            <video
                ref={videoRef}
                src={src}
                muted
                loop
                style={{ width: '100%', height: '100%', objectFit: 'cover' }} // Ensure full cover of the container
            />
            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                color: 'white',
                zIndex: 1 // Ensure text is above the overlay
            }}>
                <Typography variant="h1">{title}</Typography>
                <Typography variant="h2">{description}</Typography>
            </Box>
        </Box>
    );
};

export default VideoContent;

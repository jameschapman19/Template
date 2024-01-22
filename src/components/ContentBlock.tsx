"use client"
import React from 'react';
import { Grid, Typography, useTheme, useMediaQuery } from '@mui/material';
import Image from 'next/image';
import { motion } from 'framer-motion';

const ContentBlock = ({ title, content, direction, imageUrl, imageAlt }) => {
    const theme = useTheme();
    const matches = useMediaQuery(theme.breakpoints.up('md'));

    const imageAnimation = {
        offscreen: { x: direction === 'right' ? -100 : 100, opacity: 0 },
        onscreen: {
            x: 0,
            opacity: 1,
            transition: { type: "spring", bounce: 0.4, duration: 1 }
        }
    };

    const textAnimation = {
        offscreen: { y: 50, opacity: 0 },
        onscreen: {
            y: 0,
            opacity: 1,
            transition: { type: "spring", bounce: 0.4, duration: 1 }
        }
    };

    return (
        <Grid container spacing={2} alignItems="center" direction={matches ? (direction === 'right' ? 'row-reverse' : 'row') : 'column-reverse'}>
            <Grid item lg={6} md={6} sm={12} xs={12}>
                <motion.div initial="offscreen" whileInView="onscreen" viewport={{ once: true }} variants={imageAnimation}>
                    <Image src={imageUrl} alt={imageAlt} width={500} height={300} layout="responsive" />
                </motion.div>
            </Grid>
            <Grid item lg={6} md={6} sm={12} xs={12}>
                <motion.div initial="offscreen" whileInView="onscreen" viewport={{ once: true }} variants={textAnimation}>
                    <Typography variant="h6">{title}</Typography>
                    <Typography>{content}</Typography>
                </motion.div>
            </Grid>
        </Grid>
    );
};

export default ContentBlock;

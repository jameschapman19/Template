"use client"
import React, { ReactNode } from 'react';
import { Grid, useMediaQuery, useTheme } from '@mui/material';

interface ResponsiveSideBySideProps {
    leftComponent: ReactNode;
    rightComponent: ReactNode;
}

const ResponsiveSideBySide: React.FC<ResponsiveSideBySideProps> = ({ leftComponent, rightComponent }) => {
    const theme = useTheme();
    const isMediumUp = useMediaQuery(theme.breakpoints.up('md'));

    return (
        <Grid container spacing={2}>
            <Grid item xs={12} md={6} order={{ xs: 2, md: 1 }}>
                {isMediumUp ? leftComponent : rightComponent}
            </Grid>
            <Grid item xs={12} md={6} order={{ xs: 1, md: 2 }}>
                {isMediumUp ? rightComponent : leftComponent}
            </Grid>
        </Grid>
    );
};

export default ResponsiveSideBySide;

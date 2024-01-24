'use client';
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: {
            main: '#FFC045',
            light: '#ffd84c',
            dark: '#fbaa3e',
            contrastText: '#000',
        },
        secondary: {
            main: '#0A91AB',
            light: '#14a5c6',
            dark: '#027d92',
            contrastText: '#fff',
        },
    },
});


export default theme;
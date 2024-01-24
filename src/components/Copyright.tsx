import React from 'react';
import { Container, Box, Typography, Link, Divider, Grid } from '@mui/material';
import { grey } from '@mui/material/colors';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <Box component="footer" sx={{ backgroundColor: grey[800], color: 'white', py: 3 }}>
            <Container maxWidth="lg">
                <Divider sx={{ backgroundColor: grey[500], mb: 2 }} />

                <Grid container justifyContent="space-between" alignItems="center">
                    <Grid item>
                        <Typography variant="body2" color="inherit">
                            &copy; {currentYear} YourCompanyName. All Rights Reserved.
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Typography variant="body2" color="inherit">
                            Designed by YourName
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Link href="/privacy-policy" color="inherit" underline="hover">
                            Privacy Policy
                        </Link>
                        <span> | </span>
                        <Link href="/terms-of-service" color="inherit" underline="hover">
                            Terms of Service
                        </Link>
                    </Grid>
                </Grid>
            </Container>
        </Box>
    );
};

export default Footer;

import React from 'react';
import { Container, Box, Grid, Typography, Link, Stack, IconButton, Divider } from '@mui/material';
import { grey } from '@mui/material/colors';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import TwitterIcon from '@mui/icons-material/Twitter';
import InstagramIcon from '@mui/icons-material/Instagram';
import socials from '@/content/socials.json'; // Import the JSON file for social links
import company from '@/content/company.json';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    const getIcon = (name) => {
        switch (name) {
            case 'GitHub':
                return <GitHubIcon />;
            case 'LinkedIn':
                return <LinkedInIcon />;
            case 'Twitter':
                return <TwitterIcon />;
            case 'Instagram':
                return <InstagramIcon />;
            default:
                return null;
        }
    };

    return (
        <Box component="footer" sx={{ backgroundColor: grey[800], color: 'white', py: 3 }}>
            <Container maxWidth="lg">
                <Grid container spacing={3} justifyContent="space-between">
                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography variant="h6">Contact</Typography>
                        <Typography variant="body1">Tell us everything</Typography>
                        <Typography variant="body2">
                            Do you have any questions? Feel free to reach out.
                        </Typography>
                        <Link href="mailto:l.chapmajw@gmail.com" color="inherit" underline="hover">Let's Chat</Link>
                    </Grid>

                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography variant="h6">Company</Typography>
                        <Link href="/about" color="inherit" underline="hover">About Us</Link>
                        <br/>
                        <Link href="/contact" color="inherit" underline="hover">Contact Us</Link>
                    </Grid>

                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography variant="h6">Address</Typography>
                        <Typography variant="body2">{company.address1}</Typography>
                        <Typography variant="body2">{company.address2}</Typography>
                        <Typography variant="body2">{company.city}</Typography>
                    </Grid>
                </Grid>

                <Divider sx={{ backgroundColor: grey[500], my: 2 }} />

                <Grid container spacing={3} justifyContent="space-between" alignItems="center">
                    <Grid item>
                        <Typography variant="body2" color="inherit">
                            &copy; {currentYear} {company.companyname}. All Rights Reserved.
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Stack direction="row" spacing={2}>
                            {socials.map((social) => (
                                <IconButton key={social.name} component="a" href={social.url} target="_blank" color="inherit">
                                    {getIcon(social.name)}
                                </IconButton>
                            ))}
                        </Stack>
                    </Grid>
                    <Grid item>
                        <Link href="/privacy-policy" color="inherit" underline="hover">Privacy Policy</Link>
                        <span> | </span>
                        <Link href="/terms-of-service" color="inherit" underline="hover">Terms of Service</Link>
                    </Grid>
                </Grid>
            </Container>
        </Box>
    );
};

export default Footer;

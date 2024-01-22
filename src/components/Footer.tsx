import React from 'react';
import { Container,Box, Grid, Typography, Link, Stack, IconButton } from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import TwitterIcon from '@mui/icons-material/Twitter';
import InstagramIcon from '@mui/icons-material/Instagram';
import Image from 'next/image'

const Footer = () => {

    return (
        <Container>
            <Box component="footer" sx={{ py: 3 }}>
                <Grid container spacing={3} justifyContent="space-between">
                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography variant="h6">Contact</Typography>
                        <Typography variant="body1">Tell us everything</Typography>
                        <Typography variant="body2">
                            Do you have any question? Feel free to reach out.
                        </Typography>
                        <Link href="mailto:l.chapmajw@gmail.com">Let's Chat</Link>
                    </Grid>
                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography variant="h6">Policy</Typography>
                        <Typography>
                            <Link href="/" underline="hover">Application Security</Link>
                        </Typography>
                        <Typography>
                            <Link href="/" underline="hover">Software Principles</Link>
                        </Typography>
                    </Grid>
                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography>
                            <Link href="/" underline="hover">Support</Link>
                        </Typography>
                    </Grid>
                </Grid>

                <Grid container spacing={3} justifyContent="space-between" sx={{ pt: 3 }}>
                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography variant="h6">Address</Typography>
                        <Typography variant="body2">Rancho Santa Margarita</Typography>
                        <Typography variant="body2">2131 Elk Street</Typography>
                        <Typography variant="body2">California</Typography>
                    </Grid>
                    <Grid item lg={4} md={4} sm={6} xs={12}>
                        <Typography variant="h6">Company</Typography>
                        <Typography>
                            <Link href="/about" underline="hover">About</Link>
                        </Typography>
                        <Typography>
                            <Link href="/contact" underline="hover">Contact</Link>
                        </Typography>
                    </Grid>
                </Grid>
                <Box sx={{ borderTop: 1, borderColor: 'divider', mt: 3, pt: 3 }}>
                    <Grid container justifyContent="space-between" alignItems="center">
                        <Grid item>
                            <Link href="/" underline="none">
                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <Image
                                        src="/vercel.svg"
                                        alt="Vercel Logo"
                                        className="dark:invert"
                                        width={100}
                                        height={24}
                                        priority
                                    />
                                </Box>
                            </Link>
                        </Grid>
                        <Grid item>
                            <Stack direction="row" spacing={2}>
                                <IconButton component="a" href="https://github.com/jameschapman19" target="_blank">
                                    <GitHubIcon />
                                </IconButton>
                                <IconButton component="a" href="https://linkedin.com/in/jameswhchapman" target="_blank">
                                    <LinkedInIcon />
                                </IconButton>
                                <IconButton component="a" href="https://twitter.com/chapmajw" target="_blank">
                                    <TwitterIcon />
                                </IconButton>
                                <IconButton component="a" href="https://instagram.com/chapmajw" target="_blank">
                                    <InstagramIcon />
                                </IconButton>
                            </Stack>
                        </Grid>
                    </Grid>
                </Box>
            </Box>
        </Container>
    );
};

export default Footer;


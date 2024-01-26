"use client"
import * as React from 'react';
import { AppBar, Box, Container, Toolbar, IconButton, Typography, Button, Drawer, List, ListItem, ListItemText } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AdbIcon from '@mui/icons-material/Adb';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import Link from '@mui/material/Link';


const pages = ['About', 'Inspiration', 'Contact', 'Product'];



function ResponsiveAppBar() {
    const [mobileOpen, setMobileOpen] = React.useState(false);
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const drawer = (
        <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
            <List>
                {pages.map((page) => (
                    <Link key={page} href={`/${page.toLowerCase()}`} sx={{ textDecoration: 'none' }}>
                        <ListItem >
                            <ListItemText primary={page} />
                        </ListItem>
                    </Link>
                ))}
            </List>
        </Box>
    );

    return (
        <AppBar position="static">
            <Container>
                <Toolbar disableGutters>
                    <AdbIcon sx={{ display: 'flex', mr: 1 }} />
                    <Link href="/" sx={{ flexGrow: 1, textDecoration: 'none', color:theme.palette.primary.contrastText }}>
                        <Typography noWrap variant="h6">
                            Template
                        </Typography>
                    </Link>
                    {isMobile ? (
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', flexGrow: 1 }}>
                            <Button color="secondary" variant="contained" sx={{ ml: 2 }}>
                                Sign Up
                            </Button>
                        <IconButton
                            size="large"
                            edge="end"
                            aria-label="menu"
                            onClick={handleDrawerToggle}
                        >
                            <MenuIcon />
                        </IconButton>
                        </Box>
                    ) : (
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', flexGrow: 1 }}>
                            {pages.map((page) => (
                                    <Button key={page} href={`/${page.toLowerCase()}`} sx={{ color: theme.palette.secondary.contrastText, display: 'block', '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.18)' } }}>
                                        {page}
                                    </Button>
                            ))}
                            <Button color="secondary" variant="contained" sx={{ ml: 2 }}>
                                Sign Up
                            </Button>
                        </Box>
                    )}
                </Toolbar>
            </Container>
            <Drawer
                anchor="right"
                variant="temporary"
                open={mobileOpen}
                onClose={handleDrawerToggle}
                ModalProps={{
                    keepMounted: true, // Better open performance on mobile.
                }}
                sx={{
                    display: { xs: 'block', md: 'none' },
                    '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
                }}
            >
                {drawer}
            </Drawer>
        </AppBar>
    );
}

export default ResponsiveAppBar;

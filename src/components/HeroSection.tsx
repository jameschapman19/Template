import { Box, Typography, Button, Container } from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub'; // Import the GitHub icon

const HeroSection = () => (
    <Box sx={{
        textAlign: 'center',
        pt: 8, // Increase top padding
        pb: 8, // Increase bottom padding
        minHeight: '100vh', // Set minimum height to 100% of the viewport height
        backgroundColor: 'white', // White background color
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center', // Vertically center the content
    }}>
        <Container>
            <Typography variant="h1" sx={{
                fontWeight: 'bold',
            }}>
                Elevate Your Development Workflow
            </Typography>
            <Typography variant="h5" sx={{
                my: 2,
            }}>
                Seamlessly integrate Next.js with Flask, powered by TypeScript and Material UI.
            </Typography>
            <Typography variant="subtitle1" sx={{
                my: 2,
                color: 'text.secondary',
            }}>
                Join the developers who are enhancing their productivity with our robust template. Star us on GitHub and start building smarter, faster today.
            </Typography>
            <Box sx={{
                display: 'flex',
                justifyContent: 'center',
                gap: 2, // Add space between buttons
            }}>
                <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    href="https://github.com/jameschapman19/template"
                    target="_blank"
                    rel="noopener noreferrer"
                    startIcon={<GitHubIcon />}
                >
                    Source Code
                </Button>
                <Button
                    variant="outlined"
                    color="primary"
                    size="large"
                    href="#get-started" // Assuming you have an anchor tag or route for getting started
                >
                    Get Started
                </Button>
            </Box>
        </Container>
    </Box>
);

export default HeroSection;


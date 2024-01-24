import React from 'react';
import { Container, Typography } from '@mui/material';

const Contact = () => {
    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Contact Us
            </Typography>
            <Typography>
                Have questions or need support? Our team is here to help. Get in touch with us through the following contact details or fill out our contact form.
            </Typography>
            {/* Add more content, such as a contact form, contact details, etc. */}
        </Container>
    );
};

export default Contact;

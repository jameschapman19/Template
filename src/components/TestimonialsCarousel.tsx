"use client"
import * as React from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import MobileStepper from '@mui/material/MobileStepper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import KeyboardArrowLeft from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRight from '@mui/icons-material/KeyboardArrowRight';
import SwipeableViews from 'react-swipeable-views';
import { autoPlay } from 'react-swipeable-views-utils';

const AutoPlaySwipeableViews = autoPlay(SwipeableViews);

const testimonials = [
    {
        name: 'John Doe',
        comment: 'This service is incredible and has helped me tremendously!',
        imgPath: 'https://via.placeholder.com/100',
    },
    {
        name: 'Jane Smith',
        comment: 'Absolutely amazing! Highly recommend to anyone looking for quality service.',
        imgPath: 'https://via.placeholder.com/100',
    },
    // ... more testimonials
];

function TestimonialsCarousel() {
    const theme = useTheme();
    const [activeStep, setActiveStep] = React.useState(0);
    const maxSteps = testimonials.length;

    const handleNext = () => {
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
    };

    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };

    const handleStepChange = (step) => {
        setActiveStep(step);
    };

    return (
        <Box sx={{ textAlign: 'center', p: 4 }}>
            <Container>
            <AutoPlaySwipeableViews
                axis={theme.direction === 'rtl' ? 'x-reverse' : 'x'}
                index={activeStep}
                onChangeIndex={handleStepChange}
                enableMouseEvents
            >
                {testimonials.map((testimonial, index) => (
                    <Box key={index} sx={{ p: 2, textAlign: 'center' }}>
                        {testimonial.imgPath && (
                            <Box
                                component="img"
                                sx={{
                                    height: 100,
                                    borderRadius: '50%',
                                    mb: 2,
                                }}
                                src={testimonial.imgPath}
                                alt={testimonial.name}
                            />
                        )}
                        <Typography variant="h6">{testimonial.name}</Typography>
                        <Typography>{testimonial.comment}</Typography>
                    </Box>
                ))}
            </AutoPlaySwipeableViews>
            <MobileStepper
                steps={maxSteps}
                position="static"
                activeStep={activeStep}
                nextButton={
                    <Button
                        size="small"
                        onClick={handleNext}
                        disabled={activeStep === maxSteps - 1}
                    >
                        Next
                        {theme.direction === 'rtl' ? (
                            <KeyboardArrowLeft />
                        ) : (
                            <KeyboardArrowRight />
                        )}
                    </Button>
                }
                backButton={
                    <Button size="small" onClick={handleBack} disabled={activeStep === 0}>
                        {theme.direction === 'rtl' ? (
                            <KeyboardArrowRight />
                        ) : (
                            <KeyboardArrowLeft />
                        )}
                        Back
                    </Button>
                }
            />
            </Container>
        </Box>
    );
}

export default TestimonialsCarousel;

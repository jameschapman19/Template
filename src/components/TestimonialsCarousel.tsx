"use client"
import React from 'react';
// Import Swiper React components
import { Swiper, SwiperSlide } from 'swiper/react';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/navigation';

// import required modules
import { Autoplay, Pagination, Navigation } from 'swiper/modules';

import { Box, Typography, Container } from '@mui/material';

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

export default function TestimonialsCarousel() {
    return (
        <Container sx={{ textAlign: 'center', py: 4 }}>
            <Swiper
                spaceBetween={300}
                centeredSlides={true}
                autoplay={{
                    delay: 2500,
                    disableOnInteraction: false,
                }}
                pagination={{
                    clickable: true,
                }}
                navigation={true}
                modules={[Autoplay, Pagination, Navigation]}
                className="mySwiper"
            >
                {testimonials.map((testimonial, index) => (
                    <SwiperSlide key={index}>
                        <Box sx={{ textAlign: 'center', p: 2, padding:10 }}>
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
                    </SwiperSlide>
                ))}
            </Swiper>
        </Container>
    );
}
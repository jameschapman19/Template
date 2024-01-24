"use client"
import React from 'react';
import HeroSection from '@/components/HeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import TestimonialsCarousel from '@/components/TestimonialsCarousel';
import FAQSection from '@/components/FAQSection';
import ContactForm from '@/components/ContactForm';
import VideoContent from '@/components/VideoContent';

const Home = () => {
    return (
        <>
                <HeroSection />
                <FeaturesSection />
                <VideoContent src="/video/184069 (1080p).mp4" title="Dynamic" description="And cool" />
                <TestimonialsCarousel />
                <FAQSection />
                <ContactForm />
        </>
    );
};

export default Home;

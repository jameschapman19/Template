// page.tsx
import { Container } from '@mui/material';
import Hero from '@/components/Hero';
import ContentBlock from "@/components/ContentBlock";
import MyStory from "@/components/MyStory";
import Features from "@/components/Features";
import Content from "@/content/filler.json"

export default function Home() {
    const introContent = {
        title: "Welcome to GoodCourse",
        content: "Dive into the world of modern web development with our carefully crafted templates. Discover the synergy of MUI components and Next.js in our interactive learning platform.",
        imageUrl: "/path-to-intro-image.jpg",
        imageAlt: "Introduction"
    };

    const featuresContent = {
        title: "Why Choose This Template?",
        content: "This template is a learning platform, heavily commented to guide you through its purpose and usage.",
        imageUrl: "/path-to-features-image.jpg",
        imageAlt: "Features"
    };
    return (
        <Container>
            <Hero />
            <ContentBlock
                title={introContent.title}
                content={introContent.content}
                direction="right"
                imageUrl={introContent.imageUrl}
                imageAlt={introContent.imageAlt}
            />
            <MyStory />
            <Features />
            <ContentBlock
                title={featuresContent.title}
                content={featuresContent.content}
                direction="right"
                imageUrl={featuresContent.imageUrl}
                imageAlt={featuresContent.imageAlt}
            />
        </Container>
    );
}

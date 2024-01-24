"use client"
import { Accordion, AccordionSummary, AccordionDetails, Typography, Box, Container } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {motion, useAnimation, useInView} from 'framer-motion';
import {useEffect, useRef} from "react";
import theme from '@/theme';
const faqs = [
    { question: 'How does this work?', answer: 'Explanation about how it works.' },
    { question: 'What is the meaning of life?', answer: '42.' },
    { question: 'What is the airspeed velocity of an unladen swallow?', answer: 'Explanation about the airspeed velocity of an unladen swallow.' },
];

const FAQSection = () => {
    const controls = useAnimation();
    const ref = useRef(null);
    const isInView = useInView(ref, { amount: 0.5 });

    useEffect(() => {
        if (isInView) {
            controls.start('visible');
        }
    }, [controls, isInView]);

    const variants = {
        visible: { opacity: 1, y: 0, transition: { duration: 0.6, delay: 0.2 } },
        hidden: { opacity: 0, y: 50 },
    };

    return (
        <Box ref={ref} sx={{
            p: 4,
            textAlign: 'center',
            minHeight: '100vh',
            background: theme.palette.primary.light,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
        }}>
            <Container>
            <motion.div initial="hidden" animate={controls} variants={variants}>
                <Typography variant="h2" gutterBottom>Frequently Asked Questions</Typography>
            </motion.div>
            {faqs.map((faq, index) => (
                <motion.div initial="hidden"
                            animate={controls} variants={variants} whileHover={{ scale: 1.05 }} key={index} style={{ marginBottom: '20px' }}> {/* Added margin-bottom */}
                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>{faq.question}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Typography>{faq.answer}</Typography>
                        </AccordionDetails>
                    </Accordion>
                </motion.div>
            ))}
            </Container>
        </Box>
    );
}

export default FAQSection;

'use client'

import { Button } from "@/components/ui/button"
import Link from "next/link"
import { motion } from "framer-motion"
import { UploadCloud, Zap, Palette, ShieldCheck, CheckCircle, FileImage } from "lucide-react"

// Animation Variants
const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.8, ease: "easeOut" } },
};

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: "easeOut" } },
};

const staggerContainer = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.2,
    },
  },
};

// Page Components
function HeroSection() {
  return (
    <section className="w-full py-20 md:py-32 lg:py-40 bg-background">
      <div className="container px-4 md:px-6">
        <motion.div
          className="grid items-center gap-6 lg:grid-cols-2 lg:gap-12 xl:gap-16"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          <div className="flex flex-col justify-center space-y-6">
            <motion.div variants={fadeInUp}>
              <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl text-foreground">
                The Future of Asset Creation is Here.
              </h1>
            </motion.div>
            <motion.p 
              className="max-w-[600px] text-muted-foreground md:text-xl"
              variants={fadeInUp}
            >
              Welcome to AssetForge AI. Automate your creative workflow, eliminate tedious manual tasks, and generate stunning, on-brand assets in seconds.
            </motion.p>
            <motion.ul
              className="grid gap-2 text-lg text-muted-foreground"
              variants={fadeInUp}
            >
              <li className="flex items-center gap-2"><CheckCircle className="h-5 w-5 text-primary" /> Save Time & Reduce Costs</li>
              <li className="flex items-center gap-2"><CheckCircle className="h-5 w-5 text-primary" /> Ensure Brand Consistency</li>
              <li className="flex items-center gap-2"><CheckCircle className="h-5 w-5 text-primary" /> Scale Your Content Production</li>
            </motion.ul>
            <motion.div 
              className="flex flex-col gap-2 min-[400px]:flex-row"
              variants={fadeInUp}
            >
              <Link href="/register">
                <Button size="lg">Start Forging for Free</Button>
              </Link>
            </motion.div>
          </div>
          <motion.div variants={fadeIn}>
            <img
              src="/social-media-graphics-pack.png"
              width="600"
              height="600"
              alt="Hero Asset Collage"
              className="mx-auto aspect-square overflow-hidden rounded-xl object-cover"
            />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

function FeatureHighlight({ title, description, imageUrl, reverse = false }) {
  const imageVariants = {
    hidden: { opacity: 0, x: reverse ? -100 : 100 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  const textVariants = {
    hidden: { opacity: 0, x: reverse ? 100 : -100 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  return (
    <motion.div 
      className="mx-auto grid max-w-5xl items-center gap-6 py-12 lg:grid-cols-2 lg:gap-12"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.3 }}
      transition={{ staggerChildren: 0.2 }}
    >
      <motion.img
        src={imageUrl}
        width="550"
        height="310"
        alt={title}
        className={`mx-auto aspect-video overflow-hidden rounded-xl object-cover object-center sm:w-full ${reverse ? 'lg:order-last' : ''}`}
        variants={imageVariants}
      />
      <motion.div className="flex flex-col justify-center space-y-4" variants={textVariants}>
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">{title}</h2>
          <p className="max-w-[600px] text-muted-foreground md:text-lg">
            {description}
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}

function DetailedFeatures() {
  const features = [
    { 
      icon: UploadCloud, 
      title: "Effortless Uploads", 
      description: "Simply upload your master assets and let our system handle the rest. Secure, fast, and reliable processing.",
      iconColor: "text-blue-500 bg-blue-100 dark:bg-blue-900/50 dark:text-blue-400",
    },
    { 
      icon: Zap, 
      title: "AI-Powered Extraction", 
      description: "Leverage cutting-edge AI to automatically extract key elements from your assets, saving you hours of manual work.",
      iconColor: "text-green-500 bg-green-100 dark:bg-green-900/50 dark:text-green-400",
    },
    { 
      icon: Palette, 
      title: "Intuitive Review", 
      description: "A user-friendly interface to view, edit, and validate generated assets side-by-side with the original.",
      iconColor: "text-purple-500 bg-purple-100 dark:bg-purple-900/50 dark:text-purple-400",
    },
    { 
      icon: ShieldCheck, 
      title: "Secure & Compliant", 
      description: "Built with enterprise-grade security. Your data is encrypted and processed in a secure environment.",
      iconColor: "text-red-500 bg-red-100 dark:bg-red-900/50 dark:text-red-400",
    },
  ]

  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
      <div className="container mx-auto px-4 md:px-6">
        <motion.div 
          className="flex flex-col items-center justify-center space-y-4 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.5 }}
          variants={fadeInUp}
        >
          <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Why AssetForge AI?</h2>
          <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
            The ultimate toolkit for intelligent asset processing.
          </p>
        </motion.div>
        <motion.div 
          className="mx-auto grid max-w-7xl gap-8 py-12 sm:grid-cols-2 md:grid-cols-4 lg:gap-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
        >
          {features.map((feature, i) => (
            <motion.div key={i} className="grid gap-4 text-center p-6 rounded-lg shadow-sm bg-card" variants={fadeInUp}>
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto ${feature.iconColor}`}>
                  <feature.icon className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function UpcomingFeaturesSection() {
  const features = [
    {
      icon: Zap,
      title: "Quick Transform",
      description: "Instantly transform your existing assets with powerful AI-driven edits and enhancements.",
      iconColor: "text-blue-500 bg-blue-100 dark:bg-blue-900/50 dark:text-blue-400",
    },
    {
      icon: FileImage,
      title: "Browse Templates",
      description: "Explore a rich library of pre-made templates and formats to kickstart your creative process.",
      iconColor: "text-green-500 bg-green-100 dark:bg-green-900/50 dark:text-green-400",
    },
    {
      icon: Palette,
      title: "Brand Guidelines",
      description: "Define and manage your brand's colors, fonts, and logos to ensure every asset is always on-brand.",
      iconColor: "text-purple-500 bg-purple-100 dark:bg-purple-900/50 dark:text-purple-400",
    },
  ]

  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-background">
      <div className="container mx-auto px-4 md:px-6">
        <motion.div
          className="flex flex-col items-center justify-center space-y-4 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.5 }}
          variants={fadeInUp}
        >
          <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Upcoming Features & Enhancements</h2>
          <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
            We are constantly innovating to bring you the best experience.
          </p>
        </motion.div>
        <motion.div
          className="mx-auto grid max-w-5xl gap-8 py-12 sm:grid-cols-1 md:grid-cols-3 lg:gap-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
        >
          {features.map((feature, i) => (
            <motion.div key={i} className="grid gap-4 text-center p-6 rounded-lg shadow-sm bg-card" variants={fadeInUp}>
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto ${feature.iconColor}`}>
                  <feature.icon className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function CtaSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32">
      <motion.div 
        className="container mx-auto grid items-center justify-center gap-4 px-4 text-center md:px-6"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.5 }}
        variants={fadeInUp}
      >
        <div className="space-y-3">
          <h2 className="text-3xl font-bold tracking-tighter md:text-4xl/tight">Ready to Forge Your Assets?</h2>
          <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
            Sign up today and start automating your creative workflow. 
          </p>
        </div>
        <div className="mx-auto w-full max-w-sm space-x-2">
          <Link href="/register">
            <Button size="lg">Sign Up for Free</Button>
          </Link>
        </div>
      </motion.div>
    </section>
  )
}

function AppFooter() {
    return (
        <motion.footer 
          className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.5 }}
          variants={fadeInUp}
        >
            <p className="text-xs text-muted-foreground">&copy; 2024 AssetForge AI. All rights reserved.</p>
            <nav className="sm:ml-auto flex gap-4 sm:gap-6">
                <Link href="#" className="text-xs hover:underline underline-offset-4">
                Terms of Service
                </Link>
                <Link href="#" className="text-xs hover:underline underline-offset-4">
                Privacy
                </Link>
            </nav>
      </motion.footer>
    )
}

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-[100dvh]">
      <main className="flex-1">
        <HeroSection />
        <FeatureHighlight 
          title="Smart, AI-Powered Cropping & Repurposing"
          description="Our AI analyzes your master assets to understand the focal points, ensuring that every crop and resize is perfectly centered and context-aware. Go from a single master asset to a dozen platform-specific variations in seconds."
          imageUrl="/product-launch-graphics.png"
        />
        <FeatureHighlight 
          title="Define Your Brand, We'll Handle the Rest"
          description="Set up your brand identity, including logos, color palettes, and text styles, in our powerful admin panel. AssetForge AI ensures every generated asset is perfectly on-brand, every single time."
          imageUrl="/brand-identity-design.png"
          reverse={true}
        />
        <DetailedFeatures />
        <UpcomingFeaturesSection />
        <CtaSection />
      </main>
      <AppFooter />
    </div>
  )
}
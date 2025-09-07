import { Button } from "@/components/ui/button"
import Link from "next/link"

// Components for the landing page
function HeroSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-background">
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
          <div className="flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none text-foreground">
                Transform Your Creative Workflow with AssetForge AI
              </h1>
              <p className="max-w-[600px] text-muted-foreground md:text-xl">
                Stop wasting time on tedious manual asset resizing and repurposing. Let our AI-powered platform generate all the variations you need, instantly.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Link href="/register">
                <Button size="lg">Get Started</Button>
              </Link>
              <Link href="#features">
                <Button variant="outline" size="lg">Learn More</Button>
              </Link>
            </div>
          </div>
          <img
            src="/placeholder.svg"
            width="550"
            height="550"
            alt="Hero"
            className="mx-auto aspect-video overflow-hidden rounded-xl object-cover sm:w-full lg:order-last lg:aspect-square"
          />
        </div>
      </div>
    </section>
  )
}

function FeaturesSection() {
  return (
    <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-muted">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="space-y-2">
            <div className="inline-block rounded-lg bg-secondary px-3 py-1 text-sm">Key Features</div>
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Everything You Need to Automate Your Asset Pipeline</h2>
            <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
              From smart analysis to one-click generation, we have you covered.
            </p>
          </div>
        </div>
        <div className="mx-auto grid max-w-5xl items-center gap-6 py-12 lg:grid-cols-3 lg:gap-12">
          <div className="grid gap-1">
            <h3 className="text-xl font-bold">AI-Powered Analysis</h3>
            <p className="text-muted-foreground">
              Upload your master assets, and our AI will automatically detect key elements like faces, products, and text.
            </p>
          </div>
          <div className="grid gap-1">
            <h3 className="text-xl font-bold">One-Click Generation</h3>
            <p className="text-muted-foreground">
              Select from a library of predefined formats and generate dozens of platform-specific assets in a single click.
            </p>
          </div>
          <div className="grid gap-1">
            <h3 className="text-xl font-bold">Smart Adaptation</h3>
            <p className="text-muted-foreground">
              Our AI understands your content and intelligently crops, resizes, and adapts your assets to fit any format perfectly.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

function CtaSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32">
      <div className="container grid items-center justify-center gap-4 px-4 text-center md:px-6">
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
      </div>
    </section>
  )
}

function AppFooter() {
    return (
        <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t">
            <p className="text-xs text-muted-foreground">&copy; 2024 AssetForge AI. All rights reserved.</p>
            <nav className="sm:ml-auto flex gap-4 sm:gap-6">
                <Link href="#" className="text-xs hover:underline underline-offset-4">
                Terms of Service
                </Link>
                <Link href="#" className="text-xs hover:underline underline-offset-4">
                Privacy
                </Link>
            </nav>
      </footer>
    )
}

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-[100dvh]">
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
        <CtaSection />
      </main>
      <AppFooter />
    </div>
  )
}

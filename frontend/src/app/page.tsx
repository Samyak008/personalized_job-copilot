import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-white">
      <header className="px-6 h-16 flex items-center border-b">
        <div className="font-bold text-xl text-gray-900">ApplyWise</div>
        <div className="ml-auto flex gap-4">
          <Link href="/auth">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link href="/auth">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <section className="py-24 px-6 text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 mb-6">
            Your Personal AI <span className="text-primary">Job Application Copilot</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Optimize your resume, analyze job descriptions, and generate tailored cold emails in seconds.
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="h-12 px-8 text-base">
                Start Analyzing Now <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </section>

        <section className="bg-gray-50 py-16">
          <div className="max-w-4xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              "AI Resume Parsing",
              "Skill Gap Analysis",
              "Tailored Cold Emails",
              "Interview Strategy",
              "Resume Scoring",
              "Instant Feedback"
            ].map((feature) => (
              <div key={feature} className="flex items-center gap-3 bg-white p-4 rounded-lg shadow-sm">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="font-medium">{feature}</span>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="py-8 text-center text-gray-500 text-sm">
        © 2026 ApplyWise. All rights reserved.
      </footer>
    </div>
  );
}

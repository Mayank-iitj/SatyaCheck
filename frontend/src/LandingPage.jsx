import React, { useState } from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  ExternalLink, 
  FileCheck, 
  Layers, 
  Phone, 
  MessageSquare, 
  ChevronDown
} from 'lucide-react';
import Aurora from './Aurora';
import CurvedLoop from './CurvedLoop';
import PillNav from './PillNav';

export default function LandingPage({ onLaunchApp }) {
  const [openFaq, setOpenFaq] = useState(null);

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const faqs = [
    {
      q: "What makes SatyaCheck AI different?",
      a: "SatyaCheck AI combines cryptographic validation (Layer 1) with an advanced AI multi-model safety net (Layer 2) to deliver zero false-positives for signed publications, while catching unregistered actors, deepfakes, and phishing threats dynamically."
    },
    {
      q: "What is Neurosymbolic AI in SatyaCheck?",
      a: "We merge neural networks (deep learning for voice cloning/deepfakes) with symbolic rules (cross-referencing SEBI registries, buyback records, and official circular IDs) to ensure explainable, logical verdicts."
    },
    {
      q: "Why is explainability important for regulators?",
      a: "Regulators require an audit trail. Rather than giving a raw percentage risk score, SatyaCheck lists exact mismatches (e.g., 'Filing Mismatch: announced Rs. 5,000 buyback but registered is Rs. 3,200') to provide clear, actionable context."
    },
    {
      q: "How does the browser extension sandbox work?",
      a: "The extension runs in the background, scrubbing web content. In our Social Guard sandbox, you can simulate running the page scrubber to auto-flag coordinate pumps, scam channels, and fake notices on social networks."
    }
  ];

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 flex flex-col items-center justify-between p-6 md:p-12 overflow-x-hidden relative">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-indigo-600/5 rounded-full blur-[140px] pointer-events-none z-0"></div>
      <div className="absolute bottom-0 right-10 w-[500px] h-[500px] bg-purple-600/5 rounded-full blur-[120px] pointer-events-none z-0"></div>

      {/* PillNav Header */}
      <PillNav
        logo="/favicon.svg"
        logoAlt="SatyaCheck"
        items={[
          { label: 'Capabilities', href: '#Capabilities' },
          { label: 'FAQ', href: '#FAQ' },
          { label: 'Launch Verifier', href: '#', onClick: () => onLaunchApp('verifier') }
        ]}
        activeHref="#"
        className="z-50"
        baseColor="#0f172a" /* slate-900 */
        pillColor="#312e81" /* indigo-900 */
        hoveredPillTextColor="#ffffff"
        pillTextColor="#cbd5e1" /* slate-300 */
      />

      {/* Main Content Sections Container */}
      <main className="w-full max-w-5xl flex flex-col gap-28 py-12 z-10">
        {/* Hero Section */}
        <section className="text-center flex flex-col items-center gap-6 py-16 relative overflow-hidden rounded-3xl border border-slate-900 bg-slate-950/20 px-8">
          <div className="absolute inset-0 z-0 opacity-40">
            <Aurora
              colorStops={["#4f46e5", "#8b5cf6", "#06b6d4"]}
              blend={0.6}
              amplitude={1.0}
              speed={0.4}
            />
          </div>
          <div className="z-10 flex flex-col items-center gap-6">
            <div className="flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-xs font-semibold text-indigo-300">
              <Sparkles className="w-3.5 h-3.5" /> Presenting SatyaCheck Trust Net
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-none text-gradient-purple max-w-3xl mt-2">
              Built to Deliver Market Integrity.
            </h1>
            <p className="text-base md:text-lg text-slate-400 max-w-2xl mt-4 leading-relaxed font-medium">
              Transform core regulatory operations and protect retail investors with intelligent systems that verify provenance, cross-reference registries, and prevent modern media scams.
            </p>
            <div className="flex items-center gap-4 mt-6">
              <button 
                onClick={() => onLaunchApp('verifier')}
                className="btn-primary"
              >
                Launch Verifier Hub <ArrowRight className="w-4 h-4" />
              </button>
              <button 
                onClick={() => onLaunchApp('social')}
                className="px-6 py-3 border border-slate-800 hover:border-slate-700 hover:bg-slate-900/40 text-slate-350 hover:text-white rounded-xl text-sm font-semibold transition-all flex items-center gap-2"
              >
                Explore Sandbox <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </div>
        </section>

        {/* CurvedLoop Marquee — replaces flat text marquee */}
        <section className="w-full overflow-hidden -mt-16">
          <p className="text-xs uppercase font-bold tracking-widest text-slate-500 text-center mb-4">Trusted by top market facilitators & custodians</p>
          <CurvedLoop
            marqueeText="Securities & Exchange Board of India (SEBI) ✦ National Stock Exchange (NSE) ✦ Bombay Stock Exchange (BSE) ✦ Central Depository Services (CDSL) ✦ National Securities Depository (NSD) ✦ Reserve Bank of India (RBI) ✦"
            speed={1.5}
            curveAmount={220}
            direction="left"
            interactive={true}
            className="curved-loop-brand"
          />
        </section>

        {/* Bento Grid Capabilities */}
        <section className="flex flex-col gap-12" id="Capabilities">
          <div className="text-center max-w-2xl mx-auto flex flex-col gap-3">
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Capabilities</span>
            <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">Built for Securities Market Intelligence at Scale</h2>
            <p className="text-sm text-slate-400">Advanced detection architectures designed to verify authenticity, automate audits, and secure channels.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Card 1: Clear Logic (Span 7) */}
            <div className="bento-card md:col-span-7 flex flex-col justify-between gap-8 group">
              <div className="flex flex-col gap-3">
                <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400 w-fit">
                  <FileCheck className="w-5 h-5" />
                </div>
                <h3 className="text-xl font-bold text-white text-left">Clear Logic & Explainable Audits</h3>
                <p className="text-sm text-slate-400 leading-relaxed font-medium text-left">
                  Transparent reasoning, direct registry checks, and auditable paths. If a company buyback is declared, we instantly match the price details with registered corporate filings.
                </p>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 w-[85%] rounded-full"></div>
              </div>
            </div>

            {/* Card 2: Performance Gains (Span 5) */}
            <div className="bento-card md:col-span-5 flex flex-col justify-between gap-8">
              <div className="flex flex-col gap-3">
                <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-400 w-fit">
                  <Layers className="w-5 h-5" />
                </div>
                <h3 className="text-xl font-bold text-white text-left">Cryptographic Proof</h3>
                <p className="text-sm text-slate-400 leading-relaxed font-medium text-left">
                  C2PA metadata and digital signatures. Allow registered intermediaries to sign notices locally to bypass spoof scanners with absolute authenticity.
                </p>
              </div>
              <div className="flex items-center justify-between text-xs font-mono text-slate-500 bg-slate-950/80 p-3 rounded-lg border border-slate-900">
                <span>verification_latency</span>
                <span className="text-emerald-400 font-semibold">120ms avg</span>
              </div>
            </div>

            {/* Card 3: Voice/Video Guardian (Span 4) */}
            <div className="bento-card md:col-span-4 flex flex-col gap-3">
              <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 w-fit">
                <Phone className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white text-left">Real-Time Voice Guardian</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-medium text-left">
                Analyze streaming voice API chunks base64 sequential streams to catch AI synthetic voice changes and social engineering phone scams on the fly.
              </p>
            </div>

            {/* Card 4: WhatsApp Bot Interface (Span 4) */}
            <div className="bento-card md:col-span-4 flex flex-col gap-3">
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 w-fit">
                <MessageSquare className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white text-left">WhatsApp Bot Emulator</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-medium text-left">
                Empower retail investors to forward suspicious tips and circulars straight to our WhatsApp bot. Backed by Groq Llama 3 registry reasoning.
              </p>
            </div>

            {/* Card 5: Social Feed Scrubber (Span 4) */}
            <div className="bento-card md:col-span-4 flex flex-col gap-3">
              <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400 w-fit">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white text-left">Social Feed Scrubber</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-medium text-left">
                Interceptor extension sandbox to scrub posts, highlight fake notices, alert on unregistered advisors, and flags coordinate pump-and-dumps.
              </p>
            </div>
          </div>
        </section>

        {/* Trust Architecture Section */}
        <section className="flex flex-col gap-12 text-left" id="whyunizen">
          <div className="text-center max-w-2xl mx-auto flex flex-col gap-3">
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Why SatyaCheck?</span>
            <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">The Dual-Layer Trust Protocol</h2>
            <p className="text-sm text-slate-400">We secure regulated markets using cryptographic signatures while preserving a safety net of AI spoof detection net.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="arch-card-l1 p-8 rounded-2xl flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/35 flex items-center justify-center font-bold text-xs text-indigo-400 font-mono">L1</span>
                <h3 className="text-xl font-bold text-white">Layer 1: Cryptographic Provenance</h3>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">
                Establishes an absolute chain of trust. Issuers (SEBI, exchanges, intermediaries) cryptographically sign circulars and documents using standard public/private keys. Tampered payloads trigger immediate signature errors, securing zero false-positives.
              </p>
              <ul className="text-xs text-slate-400 flex flex-col gap-2 mt-2 font-medium">
                <li className="flex items-center gap-2">✓ Ed25519 signature validation</li>
                <li className="flex items-center gap-2">✓ Zero trust circular publications</li>
                <li className="flex items-center gap-2">✓ High-speed signature audit logs</li>
              </ul>
            </div>

            <div className="arch-card-l2 p-8 rounded-2xl flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/35 flex items-center justify-center font-bold text-xs text-purple-400 font-mono">L2</span>
                <h3 className="text-xl font-bold text-white">Layer 2: AI Multi-Model Safety Net</h3>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">
                When documents are unsigned (standard channels, WhatsApp forwards, social media posts), our multi-agent classifier scans the content for registry discrepancies, phishing patterns, voice clones, and face deepfakes.
              </p>
              <ul className="text-xs text-slate-400 flex flex-col gap-2 mt-2 font-medium">
                <li className="flex items-center gap-2">✓ Synthetic audio & deepfake net</li>
                <li className="flex items-center gap-2">✓ NLP registry mismatch identification</li>
                <li className="flex items-center gap-2">✓ Phishing & Homoglyph detection</li>
              </ul>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="flex flex-col md:grid md:grid-cols-12 gap-8 text-left" id="faq">
          <div className="md:col-span-5 flex flex-col gap-3">
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Future Answers</span>
            <h2 className="text-3xl font-bold text-white tracking-tight">Intelligence Built for Market Safety</h2>
            <p className="text-sm text-slate-400 leading-relaxed font-medium mt-2">
              Have questions about how SatyaCheck operates or integrates? Explore our frequently asked questions.
            </p>
          </div>

          <div className="md:col-span-7 flex flex-col gap-4">
            {faqs.map((faq, idx) => (
              <div key={idx} className="border border-slate-900 rounded-xl bg-slate-950/40 overflow-hidden transition-all">
                <button 
                  onClick={() => toggleFaq(idx)}
                  className="w-full flex items-center justify-between p-5 text-left font-bold text-white hover:text-indigo-400 text-sm transition-all"
                >
                  <span>{faq.q}</span>
                  <ChevronDown className={`w-4 h-4 text-slate-500 transition-all ${openFaq === idx ? 'rotate-180' : ''}`} />
                </button>
                <div className={`faq-answer ${openFaq === idx ? 'open' : ''}`} style={{ paddingBottom: openFaq === idx ? '20px' : '0px' }}>
                  <p className="px-5 text-xs text-slate-400 leading-relaxed font-medium">{faq.a}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Bottom CTA Card */}
        <section className="bento-card border border-indigo-500/20 bg-gradient-to-r from-indigo-950/10 via-slate-950 to-indigo-950/10 p-12 rounded-3xl flex flex-col items-center justify-center gap-6 text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-white tracking-tight">Build the Future of Secure Markets</h2>
          <p className="text-sm text-slate-400 max-w-lg leading-relaxed font-medium">
            Integrate the SatyaCheck trust protocol into your publication workflow today and help end retail market spoofing.
          </p>
          <button 
            onClick={() => onLaunchApp('verifier')}
            className="btn-primary px-8 py-3"
          >
            Launch Verifier Hub <ArrowRight className="w-4 h-4" />
          </button>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-5xl flex flex-col md:flex-row items-center justify-between border-t border-slate-900/60 pt-8 text-xs text-slate-500 font-medium font-mono">
        <span>© {new Date().getFullYear()} SatyaCheck Trust Network. All rights reserved.</span>
        <div className="flex gap-6 mt-4 md:mt-0">
          <a href="#Capabilities" className="hover:text-slate-350">Capabilities</a>
          <a href="#whyunizen" className="hover:text-slate-350">Why SatyaCheck?</a>
          <a href="#faq" className="hover:text-slate-350">FAQ</a>
        </div>
      </footer>
    </div>
  );
}

/**
 * LandingPage - Immersive 3D Scroll Experience
 * Inspired by HAPE.io - Central 3D object with scroll-triggered content
 */

import { useState, useEffect, useRef, Suspense, lazy } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import AuthModal from "../components/landing/AuthModal";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "../styles/landing.css";

// Lazy load Spline
const Spline = lazy(() => import('@splinetool/react-spline'));

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// ============================================
// SPLINE 3D SCENE - Robot with head rotation
// ============================================
function Spline3DScene({ activeSection, lookAtCenter }) {
  const splineRef = useRef(null);
  const headRef = useRef(null);
  const targetRotation = useRef({ x: 0, y: 0 });
  const currentRotation = useRef({ x: 0, y: 0 });
  const animationFrameRef = useRef(null);

  // Calculate target rotation based on active section
  useEffect(() => {
    // Rotation targets for each section (looking at different info cards)
    // X negative = look UP, X positive = look DOWN
    // Y negative = look LEFT, Y positive = look RIGHT
    const rotations = {
      0: { x: 0, y: 0 },           // Center - looking forward
      1: { x: -0.4, y: -0.6 },     // Top-left card (Predict) - look UP-LEFT
      2: { x: -0.4, y: 0.6 },      // Top-right card (Analyze) - look UP-RIGHT
      3: { x: 0.3, y: -0.6 },      // Bottom-left card (Optimize) - look DOWN-LEFT
      4: { x: 0.3, y: 0.6 },       // Bottom-right card (Interact) - look DOWN-RIGHT
    };

    // If lookAtCenter is true (after viewing 4th card), look at center
    if (lookAtCenter) {
      targetRotation.current = { x: 0, y: 0 };
    } else {
      targetRotation.current = rotations[activeSection] || { x: 0, y: 0 };
    }
  }, [activeSection, lookAtCenter]);

  // Smooth animation loop for head rotation
  useEffect(() => {
    const animate = () => {
      if (headRef.current) {
        // Smooth lerp towards target
        const lerpFactor = 0.08;
        currentRotation.current.x += (targetRotation.current.x - currentRotation.current.x) * lerpFactor;
        currentRotation.current.y += (targetRotation.current.y - currentRotation.current.y) * lerpFactor;

        // Apply rotation to the head
        headRef.current.rotation.x = currentRotation.current.x;
        headRef.current.rotation.y = currentRotation.current.y;
      }
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const onSplineLoad = (splineApp) => {
    splineRef.current = splineApp;

    // Try to find the head object (common names in Spline models)
    const headNames = ['Head', 'head', 'HEAD', 'Robot Head', 'Skull', 'Face'];
    for (const name of headNames) {
      const obj = splineApp.findObjectByName(name);
      if (obj) {
        headRef.current = obj;
        break;
      }
    }

    // If no head found, try to find any rotatable part
    if (!headRef.current) {
      const robot = splineApp.findObjectByName('Robot') || splineApp.findObjectByName('robot');
      if (robot) {
        headRef.current = robot;
      }
    }
  };

  return (
    <div className="spline-scene">
      <Suspense fallback={<SplineLoader />}>
        <Spline
          scene="https://prod.spline.design/zZ8QiiSBxfUozBYy/scene.splinecode"
          onLoad={onSplineLoad}
        />
      </Suspense>
      <div className="spline-glow" />
      <div className="spline-floor-glow" />
    </div>
  );
}

// Loading spinner
function SplineLoader() {
  const { t } = useTranslation();
  return (
    <div className="spline-loader">
      <div className="spline-loader__spinner" />
      <p>{t('common.loading')}</p>
    </div>
  );
}

// ============================================
// AI BRAIN FALLBACK - CSS Visual (if Spline fails)
// ============================================
function AIBrainFallback({ scrollProgress }) {
  const rotation = scrollProgress * 360;
  const scale = 1 + scrollProgress * 0.2;

  return (
    <div
      className="ai-brain"
      style={{
        transform: `rotateY(${rotation}deg) rotateX(${scrollProgress * 20}deg) scale(${scale})`,
      }}
    >
      {/* Core */}
      <div className="brain-core">
        <div className="brain-core-inner" />
        <div className="brain-core-pulse" />
        <div className="brain-core-pulse brain-core-pulse--delayed" />
      </div>

      {/* Neural rings */}
      <div className="brain-ring brain-ring-1">
        <div className="ring-dot" style={{ "--i": 0 }} />
        <div className="ring-dot" style={{ "--i": 1 }} />
        <div className="ring-dot" style={{ "--i": 2 }} />
        <div className="ring-dot" style={{ "--i": 3 }} />
        <div className="ring-dot" style={{ "--i": 4 }} />
        <div className="ring-dot" style={{ "--i": 5 }} />
      </div>

      <div className="brain-ring brain-ring-2">
        <div className="ring-dot" style={{ "--i": 0 }} />
        <div className="ring-dot" style={{ "--i": 1 }} />
        <div className="ring-dot" style={{ "--i": 2 }} />
        <div className="ring-dot" style={{ "--i": 3 }} />
        <div className="ring-dot" style={{ "--i": 4 }} />
        <div className="ring-dot" style={{ "--i": 5 }} />
        <div className="ring-dot" style={{ "--i": 6 }} />
        <div className="ring-dot" style={{ "--i": 7 }} />
      </div>

      <div className="brain-ring brain-ring-3">
        <div className="ring-dot" style={{ "--i": 0 }} />
        <div className="ring-dot" style={{ "--i": 1 }} />
        <div className="ring-dot" style={{ "--i": 2 }} />
        <div className="ring-dot" style={{ "--i": 3 }} />
      </div>

      {/* Neural connections */}
      <svg className="brain-connections" viewBox="0 0 400 400">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.2" />
          </linearGradient>
        </defs>
        {/* Dynamic neural paths */}
        <path className="neural-path" d="M200,200 Q250,150 300,180" />
        <path className="neural-path" d="M200,200 Q150,150 100,180" />
        <path className="neural-path" d="M200,200 Q250,250 300,220" />
        <path className="neural-path" d="M200,200 Q150,250 100,220" />
        <path className="neural-path" d="M200,200 Q200,100 200,50" />
        <path className="neural-path" d="M200,200 Q200,300 200,350" />
      </svg>

      {/* Floating particles */}
      <div className="brain-particles">
        {[...Array(40)].map((_, i) => (
          <div
            key={i}
            className="brain-particle"
            style={{
              "--delay": `${Math.random() * 5}s`,
              "--duration": `${3 + Math.random() * 4}s`,
              "--x": `${Math.random() * 400 - 200}px`,
              "--y": `${Math.random() * 400 - 200}px`,
              "--size": `${2 + Math.random() * 4}px`,
            }}
          />
        ))}
      </div>

      {/* Outer glow */}
      <div className="brain-glow" />
    </div>
  );
}

// ============================================
// INFO CARD - Appears on scroll
// ============================================
function InfoCard({ position, icon, title, description, isVisible, delay }) {
  return (
    <div
      className={`info-card info-card--${position} ${isVisible ? 'info-card--visible' : ''}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <div className="info-card__icon">{icon}</div>
      <h3 className="info-card__title">{title}</h3>
      <p className="info-card__desc">{description}</p>
      <div className="info-card__connector" />
    </div>
  );
}

// ============================================
// MAIN LANDING PAGE
// ============================================
export default function LandingPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [activeSection, setActiveSection] = useState(0);
  const [lookAtCenter, setLookAtCenter] = useState(false);
  const [showCTA, setShowCTA] = useState(false);
  const containerRef = useRef(null);
  const centerTimerRef = useRef(null);
  const { isAuthenticated, isAdmin } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // When reaching section 4, look at card first, then center after delay
  useEffect(() => {
    if (activeSection === 4) {
      // First look at 4th card, then after 1 second look at center
      setLookAtCenter(false);
      setShowCTA(false);

      centerTimerRef.current = setTimeout(() => {
        setLookAtCenter(true);
        // Show CTA text after robot looks at center
        setTimeout(() => setShowCTA(true), 500);
      }, 1000);
    } else {
      setLookAtCenter(false);
      setShowCTA(false);
      if (centerTimerRef.current) {
        clearTimeout(centerTimerRef.current);
      }
    }

    return () => {
      if (centerTimerRef.current) {
        clearTimeout(centerTimerRef.current);
      }
    };
  }, [activeSection]);

  // Setup scroll animations
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Main scroll progress
    const scrollHandler = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = Math.min(scrollTop / docHeight, 1);
      setScrollProgress(progress);

      // Determine active section (0-4)
      const section = Math.min(Math.floor(progress * 5), 4);
      setActiveSection(section);
    };

    window.addEventListener('scroll', scrollHandler);

    // GSAP ScrollTrigger animations
    const sections = gsap.utils.toArray('.scroll-section');

    sections.forEach((section, i) => {
      ScrollTrigger.create({
        trigger: section,
        start: 'top center',
        end: 'bottom center',
        onEnter: () => setActiveSection(i),
        onEnterBack: () => setActiveSection(i),
      });
    });

    return () => {
      window.removeEventListener('scroll', scrollHandler);
      ScrollTrigger.getAll().forEach(t => t.kill());
    };
  }, []);

  const handleStart = () => {
    if (isAuthenticated) {
      navigate(isAdmin ? "/admin" : "/user");
    } else {
      setModalOpen(true);
    }
  };

  // Info cards data - localized
  const infoCards = [
    {
      position: "top-left",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: t('landing.features.forecast.title'),
      description: t('landing.features.forecast.description'),
    },
    {
      position: "top-right",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 6v6l4 2" />
        </svg>
      ),
      title: t('landing.features.analysis.title'),
      description: t('landing.features.analysis.description'),
    },
    {
      position: "bottom-left",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
      ),
      title: t('landing.features.optimization.title'),
      description: t('landing.features.optimization.description'),
    },
    {
      position: "bottom-right",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" />
        </svg>
      ),
      title: t('landing.features.dialog.title'),
      description: t('landing.features.dialog.description'),
    },
  ];

  return (
    <div className="landing-immersive" ref={containerRef}>
      {/* Fixed navbar */}
      <nav className="nav-immersive">
        <div className="nav__logo">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <circle cx="18" cy="18" r="16" stroke="currentColor" strokeWidth="1.5" />
            <circle cx="18" cy="18" r="6" fill="currentColor" />
            <circle cx="18" cy="8" r="2" fill="currentColor" />
            <circle cx="18" cy="28" r="2" fill="currentColor" />
            <circle cx="8" cy="18" r="2" fill="currentColor" />
            <circle cx="28" cy="18" r="2" fill="currentColor" />
          </svg>
          <span>Forecast AI</span>
        </div>
        <div className="nav__progress">
          <div
            className="nav__progress-bar"
            style={{ transform: `scaleX(${scrollProgress})` }}
          />
        </div>
        <button className="nav__cta" onClick={handleStart}>
          {t('landing.getStarted')}
        </button>
      </nav>

      {/* Fixed center scene */}
      <div className="scene-container">
        {/* 3D Robot from Spline */}
        <Spline3DScene activeSection={activeSection} lookAtCenter={lookAtCenter} />

        {/* Info cards around the brain */}
        {infoCards.map((card, i) => (
          <InfoCard
            key={i}
            {...card}
            isVisible={activeSection >= i + 1}
            delay={i * 100}
          />
        ))}

        {/* Center text - changes based on scroll */}
        <div className="scene-text">
          {activeSection === 0 && (
            <div className="scene-text__content scene-text__content--hero">
              <h1>
                <span>{t('landing.heroTitle1')}</span>
                <span className="gradient-text">{t('landing.heroTitle2')}</span>
              </h1>
              <p>{t('landing.scrollToExplore')}</p>
              <div className="scroll-indicator">
                <div className="scroll-indicator__mouse">
                  <div className="scroll-indicator__wheel" />
                </div>
              </div>
            </div>
          )}

          {showCTA && (
            <div className="scene-text__content scene-text__content--cta">
              <h2>{t('landing.cta.title')}</h2>
              <button className="cta-button" onClick={handleStart}>
                <span>{t('landing.cta.button')}</span>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Scroll sections (invisible, just for scroll tracking) */}
      <div className="scroll-sections">
        <section className="scroll-section scroll-section--hero">
          <div className="section-content">
            <span className="section-number">01</span>
          </div>
        </section>

        <section className="scroll-section scroll-section--predict">
          <div className="section-content">
            <span className="section-number">02</span>
            <h2>{t('landing.sections.predict.title')}</h2>
            <p>{t('landing.sections.predict.description')}</p>
          </div>
        </section>

        <section className="scroll-section scroll-section--analyze">
          <div className="section-content">
            <span className="section-number">03</span>
            <h2>{t('landing.sections.understand.title')}</h2>
            <p>{t('landing.sections.understand.description')}</p>
          </div>
        </section>

        <section className="scroll-section scroll-section--optimize">
          <div className="section-content">
            <span className="section-number">04</span>
            <h2>{t('landing.sections.optimize.title')}</h2>
            <p>{t('landing.sections.optimize.description')}</p>
          </div>
        </section>

        <section className="scroll-section scroll-section--cta">
          <div className="section-content">
            <span className="section-number">05</span>
          </div>
        </section>
      </div>

      {/* Side scroll progress */}
      <div className="scroll-progress-vertical">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`progress-dot ${activeSection >= i ? 'progress-dot--active' : ''}`}
          />
        ))}
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={() => setModalOpen(false)}
      />
    </div>
  );
}

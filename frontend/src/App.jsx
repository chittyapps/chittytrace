import { useState, useEffect } from 'react'
import Hero from './components/Hero'
import Features from './components/Features'
import Stats from './components/Stats'
import Testimonials from './components/Testimonials'
import Pricing from './components/Pricing'
import Footer from './components/Footer'
import Navbar from './components/Navbar'

function App() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <Navbar scrolled={scrolled} />
      <Hero />
      <Features />
      <Stats />
      <Testimonials />
      <Pricing />
      <Footer />
    </div>
  )
}

export default App

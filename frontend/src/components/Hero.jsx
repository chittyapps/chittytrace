import { ArrowRight, Star, Zap, Shield, Globe, Sparkles, Rocket } from 'lucide-react'
import { useState, useEffect } from 'react'

const Hero = () => {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <section className="relative pt-32 pb-20 px-4 overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-transparent to-purple-50 opacity-70"></div>
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-40 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '4s'}}></div>
      </div>

      <div className="relative max-w-7xl mx-auto">
        <div className="text-center">
          <div className={`inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-full mb-8 border border-blue-100 shadow-lg transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <Sparkles className="w-5 h-5 text-blue-600 mr-2 animate-pulse" />
            <span className="text-sm font-medium bg-gradient-to-r from-blue-700 to-purple-700 bg-clip-text text-transparent">✨ New: AI-Powered Development Suite</span>
            <Rocket className="w-5 h-5 text-purple-600 ml-2 animate-bounce" />
          </div>

          <h1 className={`text-6xl md:text-8xl font-bold mb-8 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`} style={{animationDelay: '200ms'}}>
            Build the Future
            <br />
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-pulse-slow">Today</span>
          </h1>

          <p className={`text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`} style={{animationDelay: '400ms'}}>
            Transform your wildest ideas into reality with our next-generation platform.
            Join the revolution that's reshaping how developers build.
          </p>

          <div className={`flex flex-col sm:flex-row gap-6 justify-center mb-16 transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`} style={{animationDelay: '600ms'}}>
            <button className="group px-10 py-5 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white rounded-full font-semibold text-lg hover:shadow-2xl transition-all transform hover:scale-105 flex items-center justify-center relative overflow-hidden">
              <span className="absolute inset-0 bg-gradient-to-r from-blue-700 via-purple-700 to-pink-700 opacity-0 group-hover:opacity-100 transition-opacity"></span>
              <span className="relative flex items-center">
                Start Building Free
                <ArrowRight className="ml-3 w-6 h-6 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <button className="px-10 py-5 bg-white/80 backdrop-blur-sm text-gray-800 rounded-full font-semibold text-lg border-2 border-gray-200 hover:border-purple-300 hover:shadow-xl transition-all hover:bg-white/90">
              Watch Demo
            </button>
          </div>

          <div className={`flex flex-wrap items-center justify-center gap-8 mb-20 transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`} style={{animationDelay: '800ms'}}>
            <div className="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <div className="flex -space-x-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 border-3 border-white shadow-lg"></div>
                ))}
              </div>
              <span className="ml-4 text-sm font-semibold text-gray-700">50k+ Developers</span>
            </div>
            <div className="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <div className="flex mr-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Star key={i} className="w-6 h-6 text-yellow-500 fill-current" />
                ))}
              </div>
              <span className="text-sm font-semibold text-gray-700">4.9/5 Rating</span>
            </div>
            <div className="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <Zap className="w-6 h-6 text-green-500 mr-2" />
              <span className="text-sm font-semibold text-gray-700">99.9% Uptime</span>
            </div>
          </div>

          <div className={`relative rounded-3xl overflow-hidden shadow-2xl max-w-6xl mx-auto transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`} style={{animationDelay: '1000ms'}}>
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/30 to-purple-600/30"></div>
            <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-black p-10 md:p-16">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                <div className="text-center group">
                  <Shield className="w-16 h-16 text-blue-400 mx-auto mb-6 group-hover:scale-110 transition-transform" />
                  <h3 className="text-white font-bold text-xl mb-3">Military-Grade Security</h3>
                  <p className="text-gray-300">Zero-trust architecture with end-to-end encryption</p>
                </div>
                <div className="text-center group">
                  <Globe className="w-16 h-16 text-purple-400 mx-auto mb-6 group-hover:scale-110 transition-transform" />
                  <h3 className="text-white font-bold text-xl mb-3">Global Edge Network</h3>
                  <p className="text-gray-300">Deploy to 200+ locations worldwide instantly</p>
                </div>
                <div className="text-center group">
                  <Zap className="w-16 h-16 text-green-400 mx-auto mb-6 group-hover:scale-110 transition-transform" />
                  <h3 className="text-white font-bold text-xl mb-3">Lightning Performance</h3>
                  <p className="text-gray-300">Sub-100ms response times guaranteed</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced floating elements */}
      <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-blue-400 rounded-full opacity-10 blur-3xl animate-pulse-slow"></div>
      <div className="absolute -top-20 -right-20 w-80 h-80 bg-purple-400 rounded-full opacity-10 blur-3xl animate-pulse-slow" style={{animationDelay: '1s'}}></div>
      <div className="absolute top-1/2 left-1/4 w-40 h-40 bg-pink-400 rounded-full opacity-5 blur-2xl animate-float" style={{animationDelay: '3s'}}></div>
    </section>
  )
}

export default Hero
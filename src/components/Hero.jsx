import { ArrowRight, Star, Zap, Shield, Globe } from 'lucide-react'

const Hero = () => {
  return (
    <section className="relative pt-32 pb-20 px-4 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-transparent to-purple-50 opacity-70"></div>

      <div className="relative max-w-7xl mx-auto">
        <div className="text-center">
          <div className="inline-flex items-center px-4 py-2 bg-blue-50 rounded-full mb-6">
            <Zap className="w-4 h-4 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-700">New: AI-Powered Analytics</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent">
            Build Something
            <br />
            Amazing Today
          </h1>

          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Transform your ideas into reality with our cutting-edge platform.
            Trusted by thousands of developers worldwide.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full font-medium hover:shadow-xl transition-all transform hover:scale-105 flex items-center justify-center">
              Start Free Trial
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
            <button className="px-8 py-4 bg-white text-gray-700 rounded-full font-medium border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all">
              Watch Demo
            </button>
          </div>

          <div className="flex items-center justify-center space-x-8 mb-16">
            <div className="flex items-center">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 border-2 border-white"></div>
                ))}
              </div>
              <span className="ml-3 text-sm text-gray-600">10k+ Users</span>
            </div>
            <div className="flex items-center">
              <div className="flex">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <span className="ml-2 text-sm text-gray-600">4.9/5 Rating</span>
            </div>
          </div>

          <div className="relative rounded-2xl overflow-hidden shadow-2xl max-w-5xl mx-auto">
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/20 to-purple-600/20"></div>
            <div className="bg-gray-900 p-8 md:p-12">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="text-center">
                  <Shield className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                  <h3 className="text-white font-semibold mb-2">Secure by Default</h3>
                  <p className="text-gray-400 text-sm">Enterprise-grade security built in</p>
                </div>
                <div className="text-center">
                  <Globe className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                  <h3 className="text-white font-semibold mb-2">Global Scale</h3>
                  <p className="text-gray-400 text-sm">Deploy worldwide in seconds</p>
                </div>
                <div className="text-center">
                  <Zap className="w-12 h-12 text-green-400 mx-auto mb-4" />
                  <h3 className="text-white font-semibold mb-2">Lightning Fast</h3>
                  <p className="text-gray-400 text-sm">Optimized for peak performance</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-blue-400 rounded-full opacity-10 blur-3xl"></div>
      <div className="absolute -top-10 -right-10 w-60 h-60 bg-purple-400 rounded-full opacity-10 blur-3xl"></div>
    </section>
  )
}

export default Hero
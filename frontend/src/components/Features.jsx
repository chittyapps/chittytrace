import { Code, Palette, Zap, Shield, Users, Globe } from 'lucide-react'

const Features = () => {
  const features = [
    {
      icon: <Code className="w-6 h-6" />,
      title: "Clean Code",
      description: "Write beautiful, maintainable code with modern best practices"
    },
    {
      icon: <Palette className="w-6 h-6" />,
      title: "Stunning Design",
      description: "Pixel-perfect designs that adapt to any screen size"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Lightning Fast",
      description: "Optimized performance with lazy loading and code splitting"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Secure",
      description: "Enterprise-grade security with built-in protection"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Team Collaboration",
      description: "Work together seamlessly with real-time updates"
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Global CDN",
      description: "Deploy anywhere with automatic scaling"
    }
  ]

  return (
    <section id="features" className="py-20 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Everything you need to build modern web applications
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="group p-6 rounded-xl border border-gray-100 hover:border-blue-200 hover:shadow-xl transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Features
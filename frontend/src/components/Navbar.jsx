import { useState } from 'react'
import { Menu, X } from 'lucide-react'

const Navbar = ({ scrolled }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className={`fixed w-full z-50 transition-all duration-300 ${
      scrolled ? 'bg-white/95 backdrop-blur-md shadow-lg' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              TechFlow
            </span>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-gray-700 hover:text-blue-600 transition-colors">Features</a>
            <a href="#pricing" className="text-gray-700 hover:text-blue-600 transition-colors">Pricing</a>
            <a href="#testimonials" className="text-gray-700 hover:text-blue-600 transition-colors">Testimonials</a>
            <button className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full hover:shadow-lg transition-all transform hover:scale-105">
              Get Started
            </button>
          </div>

          <div className="md:hidden">
            <button onClick={() => setIsOpen(!isOpen)}>
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {isOpen && (
          <div className="md:hidden bg-white rounded-lg shadow-lg mt-2 p-4">
            <a href="#features" className="block py-2 text-gray-700 hover:text-blue-600">Features</a>
            <a href="#pricing" className="block py-2 text-gray-700 hover:text-blue-600">Pricing</a>
            <a href="#testimonials" className="block py-2 text-gray-700 hover:text-blue-600">Testimonials</a>
            <button className="w-full mt-4 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full">
              Get Started
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
import { Star } from 'lucide-react'

const Testimonials = () => {
  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "CEO at TechStart",
      content: "This platform has transformed how we build and deploy applications. The speed and reliability are unmatched.",
      avatar: "SJ"
    },
    {
      name: "Michael Chen",
      role: "Lead Developer",
      content: "The developer experience is incredible. Everything just works, and the performance optimizations are outstanding.",
      avatar: "MC"
    },
    {
      name: "Emily Rodriguez",
      role: "Product Manager",
      content: "Our team's productivity has increased by 300%. The collaboration features are exactly what we needed.",
      avatar: "ER"
    }
  ]

  return (
    <section id="testimonials" className="py-20 px-4 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">What Our Users Say</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Join thousands of satisfied developers and teams
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star key={star} className="w-5 h-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-600 mb-6">"{testimonial.content}"</p>
              <div className="flex items-center">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold mr-4">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold">{testimonial.name}</div>
                  <div className="text-sm text-gray-500">{testimonial.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Testimonials
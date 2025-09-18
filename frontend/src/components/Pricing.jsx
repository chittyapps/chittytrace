import { Check } from 'lucide-react'

const Pricing = () => {
  const plans = [
    {
      name: "Starter",
      price: "$9",
      description: "Perfect for side projects",
      features: [
        "Up to 3 projects",
        "1GB storage",
        "Community support",
        "Basic analytics",
        "SSL certificates"
      ]
    },
    {
      name: "Pro",
      price: "$29",
      description: "For professional developers",
      features: [
        "Unlimited projects",
        "10GB storage",
        "Priority support",
        "Advanced analytics",
        "Custom domains",
        "Team collaboration",
        "API access"
      ],
      popular: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large teams",
      features: [
        "Everything in Pro",
        "Unlimited storage",
        "24/7 dedicated support",
        "Custom integrations",
        "SLA guarantee",
        "Advanced security",
        "Training sessions"
      ]
    }
  ]

  return (
    <section id="pricing" className="py-20 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Choose the perfect plan for your needs
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div key={index} className={`relative p-8 rounded-2xl border ${
              plan.popular
                ? 'border-blue-600 shadow-2xl scale-105'
                : 'border-gray-200 shadow-lg'
            }`}>
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-gray-600 mb-4">{plan.description}</p>
                <div className="text-5xl font-bold mb-4">
                  {plan.price}
                  {plan.price !== "Custom" && <span className="text-base text-gray-600 font-normal">/month</span>}
                </div>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start">
                    <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <button className={`w-full py-3 rounded-full font-semibold transition-all ${
                plan.popular
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}>
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Pricing
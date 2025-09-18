const Stats = () => {
  const stats = [
    { number: "10K+", label: "Active Users" },
    { number: "500+", label: "Projects Created" },
    { number: "99.9%", label: "Uptime" },
    { number: "24/7", label: "Support" }
  ]

  return (
    <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                {stat.number}
              </div>
              <div className="text-blue-100">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Stats
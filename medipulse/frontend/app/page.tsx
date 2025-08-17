"use client"

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, Sparkles, Brain, Shield, Zap, ArrowRight, FileText, CheckCircle2 } from 'lucide-react'

export default function LandingPage() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [extractedCount, setExtractedCount] = useState(1247)
  const [timeSaved, setTimeSaved] = useState(282)

  // Animate counters
  useEffect(() => {
    const interval = setInterval(() => {
      setExtractedCount(prev => prev + Math.floor(Math.random() * 3))
      setTimeSaved(prev => prev + Math.random() * 0.5)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-purple-400/20 rounded-full"
            initial={{ 
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight 
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            transition={{
              duration: Math.random() * 20 + 10,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        ))}
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex justify-between items-center px-8 py-6">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center space-x-2"
        >
          <Brain className="w-8 h-8 text-purple-400" />
          <span className="text-2xl font-bold text-white">MediPulse</span>
        </motion.div>
        
        <motion.button
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-6 py-2 bg-purple-600 text-white rounded-full font-semibold hover:bg-purple-500 transition-colors"
        >
          Request Demo
        </motion.button>
      </nav>

      {/* Hero Section */}
      <div className="relative z-10 flex flex-col items-center justify-center px-8 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center max-w-4xl"
        >
          <div className="inline-flex items-center px-4 py-2 bg-purple-600/20 rounded-full mb-6 backdrop-blur-sm">
            <Sparkles className="w-4 h-4 text-yellow-400 mr-2" />
            <span className="text-purple-200 text-sm font-medium">
              YC W25 - AI Agents for Healthcare
            </span>
          </div>

          <h1 className="text-6xl font-bold text-white mb-6 leading-tight">
            Extract Medical Data in
            <motion.span
              className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 ml-3"
              animate={{ 
                backgroundPosition: ["0%", "100%", "0%"],
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              30 Seconds
            </motion.span>
          </h1>

          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Watch AI agents collaborate in real-time to extract, validate, and structure 
            medical records with 95% accuracy. Turn 6 hours of manual work into seconds.
          </p>

          {/* Live Stats */}
          <div className="flex justify-center space-x-8 mb-12">
            <motion.div 
              className="text-center"
              whileHover={{ scale: 1.05 }}
            >
              <div className="text-3xl font-bold text-purple-400">
                {extractedCount.toLocaleString()}
              </div>
              <div className="text-sm text-gray-400">Documents Processed</div>
            </motion.div>
            <motion.div 
              className="text-center"
              whileHover={{ scale: 1.05 }}
            >
              <div className="text-3xl font-bold text-green-400">95%</div>
              <div className="text-sm text-gray-400">Accuracy Rate</div>
            </motion.div>
            <motion.div 
              className="text-center"
              whileHover={{ scale: 1.05 }}
            >
              <div className="text-3xl font-bold text-blue-400">
                {timeSaved.toFixed(0)}h
              </div>
              <div className="text-sm text-gray-400">Time Saved</div>
            </motion.div>
          </div>

          {/* Demo Upload Area */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="relative"
          >
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="relative group cursor-pointer"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity" />
              
              <div className="relative bg-slate-800/50 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-12">
                <input 
                  type="file" 
                  className="hidden" 
                  id="file-upload"
                  accept="image/*,.pdf"
                  onChange={() => setIsProcessing(true)}
                />
                <label 
                  htmlFor="file-upload"
                  className="flex flex-col items-center cursor-pointer"
                >
                  <motion.div
                    animate={{ 
                      y: isProcessing ? -10 : [0, -5, 0],
                      rotate: isProcessing ? 360 : 0
                    }}
                    transition={{ 
                      y: { duration: 2, repeat: Infinity },
                      rotate: { duration: 1, repeat: isProcessing ? Infinity : 0 }
                    }}
                  >
                    <Upload className="w-16 h-16 text-purple-400 mb-4" />
                  </motion.div>
                  
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {isProcessing ? "Processing with AI Agents..." : "Drop Medical Document Here"}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    Support: Lab Reports, Patient Forms, Prescriptions, Discharge Summaries
                  </p>
                </label>

                {/* Processing Animation */}
                <AnimatePresence>
                  {isProcessing && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-6 space-y-3"
                    >
                      {["Scanner Agent", "Medical Expert Agent", "Validator Agent"].map((agent, i) => (
                        <motion.div
                          key={agent}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.5 }}
                          className="flex items-center space-x-3"
                        >
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity }}
                            className={`w-2 h-2 rounded-full ${
                              i === 0 ? 'bg-blue-400' : 
                              i === 1 ? 'bg-purple-400' : 'bg-green-400'
                            }`}
                          />
                          <span className="text-gray-300 text-sm">{agent} analyzing...</span>
                          {i < 2 && (
                            <CheckCircle2 className="w-4 h-4 text-green-400 ml-auto" />
                          )}
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>

            {/* Try Demo Button */}
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => window.location.href = '/dashboard'}
              className="mt-8 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full font-semibold text-lg hover:shadow-2xl hover:shadow-purple-500/30 transition-all flex items-center mx-auto"
            >
              Try Live Demo
              <ArrowRight className="ml-2 w-5 h-5" />
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 max-w-5xl"
        >
          {[
            {
              icon: Brain,
              title: "Multi-Agent System",
              description: "3 specialized AI agents work together to extract, validate, and structure your data",
              color: "from-blue-500 to-purple-500"
            },
            {
              icon: Zap,
              title: "Real-Time Processing",
              description: "Watch agents think and collaborate with live WebSocket streaming",
              color: "from-purple-500 to-pink-500"
            },
            {
              icon: Shield,
              title: "HIPAA Ready",
              description: "Enterprise-grade security with full audit trails and compliance features",
              color: "from-pink-500 to-red-500"
            }
          ].map((feature, i) => (
            <motion.div
              key={i}
              whileHover={{ scale: 1.05, y: -5 }}
              className="relative group"
            >
              <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} rounded-xl blur-lg opacity-30 group-hover:opacity-50 transition-opacity`} />
              <div className="relative bg-slate-800/50 backdrop-blur-xl border border-purple-500/20 rounded-xl p-6">
                <feature.icon className="w-10 h-10 text-purple-400 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  )
}
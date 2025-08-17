"use client"

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, Brain, Eye, Shield, Sparkles, 
  FileText, Clock, CheckCircle, AlertCircle,
  Download, RefreshCw, ChevronRight, Loader2,
  Activity, Zap
} from 'lucide-react'
import { WebSocketManager } from '../../lib/websocket'
import { apiClient } from '../../lib/api'

// WebSocket hook
function useWebSocket(sessionId: string | null) {
  const [messages, setMessages] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const wsManager = useRef<WebSocketManager | null>(null)

  useEffect(() => {
    if (!sessionId) return

    const wsUrl = apiClient.getWebSocketUrl(sessionId)
    wsManager.current = new WebSocketManager(wsUrl)

    wsManager.current.on('message', (data: any) => {
      setMessages(prev => [...prev, data])
    })

    wsManager.current.connect()
      .then(() => setIsConnected(true))
      .catch(console.error)

    return () => {
      wsManager.current?.disconnect()
      setIsConnected(false)
    }
  }, [sessionId])

  return { messages, isConnected, wsManager: wsManager.current }
}

// Simple agent visualization without ReactFlow dependency
const AgentNode = ({ agent, isActive, confidence }: { 
  agent: string, 
  isActive: boolean, 
  confidence?: number 
}) => {
  const getIcon = () => {
    switch (agent) {
      case 'Scanner Agent': return <Eye className="w-4 h-4" />
      case 'Medical Expert Agent': return <Brain className="w-4 h-4" />
      case 'Validator Agent': return <Shield className="w-4 h-4" />
      default: return <Sparkles className="w-4 h-4" />
    }
  }

  const getColor = () => {
    switch (agent) {
      case 'Scanner Agent': return 'from-blue-500 to-purple-500'
      case 'Medical Expert Agent': return 'from-purple-500 to-pink-500'  
      case 'Validator Agent': return 'from-green-500 to-blue-500'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  return (
    <motion.div
      animate={{ 
        scale: isActive ? 1.05 : 1,
        opacity: isActive ? 1 : 0.7
      }}
      className={`
        relative p-4 rounded-xl bg-gradient-to-r ${getColor()}
        ${isActive ? 'ring-2 ring-white/50 shadow-lg' : ''}
        transition-all duration-300
      `}
    >
      <div className="flex items-center space-x-2 text-white">
        {getIcon()}
        <span className="text-sm font-medium">{agent}</span>
      </div>
      {confidence !== undefined && (
        <div className="mt-2">
          <div className="w-full bg-black/20 rounded-full h-1">
            <motion.div
              className="h-1 bg-white rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${confidence * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <span className="text-xs text-white/80 mt-1 block">
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      )}
    </motion.div>
  )
}

export default function Dashboard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [extractedData, setExtractedData] = useState<any>(null)
  const [currentAgent, setCurrentAgent] = useState<string>("")
  const [confidence, setConfidence] = useState(0)
  const [documentPreview, setDocumentPreview] = useState<string>("")
  
  const { messages, isConnected } = useWebSocket(sessionId)

  // Process WebSocket messages
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      
      if (lastMessage.type === 'agent_update') {
        setCurrentAgent(lastMessage.agent)
        if (lastMessage.confidence) {
          setConfidence(lastMessage.confidence * 100)
        }
      } else if (lastMessage.type === 'processing_complete') {
        setIsProcessing(false)
        setExtractedData(lastMessage.extracted_data)
        setConfidence(lastMessage.confidence_score * 100)
      }
    }
  }, [messages])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setSelectedFile(file)
    setIsProcessing(true)

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setDocumentPreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)

    try {
      // Upload via API client
      const result = await apiClient.uploadDocument(file)
      setSessionId(result.session_id)
    } catch (error) {
      console.error('Upload failed:', error)
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Header */}
      <div className="border-b border-purple-800/30 backdrop-blur-xl bg-black/20">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-purple-400" />
            <h1 className="text-2xl font-bold text-white">MediPulse Dashboard</h1>
            <div className="ml-6 flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
              <span className="text-sm text-gray-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-500 transition-colors"
            >
              Export Results
            </motion.button>
          </div>
        </div>
      </div>

      <div className="flex h-[calc(100vh-73px)]">
        {/* Left Panel - Document Upload & Preview */}
        <div className="w-1/2 border-r border-purple-800/30 p-6">
          <div className="h-full flex flex-col space-y-4">
            {/* Upload Area */}
            <motion.div
              whileHover={{ scale: 1.01 }}
              className="relative"
            >
              <input
                type="file"
                onChange={handleFileUpload}
                accept="image/*,.pdf"
                className="hidden"
                id="file-input"
              />
              <label
                htmlFor="file-input"
                className="block w-full p-8 border-2 border-dashed border-purple-500/50 rounded-xl hover:border-purple-400 transition-colors cursor-pointer bg-purple-900/20"
              >
                <div className="text-center">
                  <Upload className="w-12 h-12 text-purple-400 mx-auto mb-3" />
                  <p className="text-white font-medium">
                    {selectedFile ? selectedFile.name : 'Drop medical document here'}
                  </p>
                  <p className="text-gray-400 text-sm mt-1">
                    PDF, JPEG, PNG, TIFF supported
                  </p>
                </div>
              </label>
            </motion.div>

            {/* Document Preview */}
            <div className="flex-1 bg-black/30 rounded-xl p-4 overflow-hidden">
              {documentPreview ? (
                <img 
                  src={documentPreview} 
                  alt="Document preview"
                  className="w-full h-full object-contain rounded-lg"
                />
              ) : (
                <div className="h-full flex items-center justify-center">
                  <FileText className="w-24 h-24 text-gray-600" />
                </div>
              )}
            </div>

            {/* Processing Status */}
            {isProcessing && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-purple-900/30 rounded-xl p-4 backdrop-blur-xl"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-white font-medium">Processing Document</span>
                  <span className="text-purple-400">{confidence.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${confidence}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                <div className="mt-3 flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                  <span className="text-sm text-gray-400">{currentAgent} analyzing...</span>
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Right Panel - Agent Workflow & Results */}
        <div className="w-1/2 p-6">
          <div className="h-full flex flex-col space-y-4">
            {/* Agent Workflow Visualization */}
            <div className="h-64 bg-black/30 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-medium">Agent Collaboration</h3>
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-green-400 animate-pulse" />
                  <span className="text-sm text-gray-400">Live</span>
                </div>
              </div>
              
              <div className="h-48 flex items-center justify-center space-x-4">
                <AgentNode 
                  agent="Scanner Agent" 
                  isActive={currentAgent === "Scanner Agent"}
                  confidence={currentAgent === "Scanner Agent" ? confidence / 100 : undefined}
                />
                <ChevronRight className="text-gray-400" />
                <AgentNode 
                  agent="Medical Expert Agent" 
                  isActive={currentAgent === "Medical Expert Agent"}
                  confidence={currentAgent === "Medical Expert Agent" ? confidence / 100 : undefined}
                />
                <ChevronRight className="text-gray-400" />
                <AgentNode 
                  agent="Validator Agent" 
                  isActive={currentAgent === "Validator Agent"}
                  confidence={currentAgent === "Validator Agent" ? confidence / 100 : undefined}
                />
              </div>
            </div>

            {/* Agent Messages */}
            <div className="flex-1 bg-black/30 rounded-xl p-4 overflow-y-auto">
              <h3 className="text-white font-medium mb-3">Agent Communication</h3>
              <div className="space-y-2">
                <AnimatePresence>
                  {messages.map((msg, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="bg-purple-900/20 rounded-lg p-3 border border-purple-500/20"
                    >
                      <div className="flex items-start space-x-2">
                        <Sparkles className="w-4 h-4 text-purple-400 mt-0.5" />
                        <div className="flex-1">
                          <div className="text-sm text-purple-300 font-medium">
                            {msg.agent || 'System'}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {msg.action}: {JSON.stringify(msg.data).substring(0, 100)}...
                          </div>
                        </div>
                        {msg.confidence && (
                          <div className="text-xs text-green-400">
                            {(msg.confidence * 100).toFixed(0)}%
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Extracted Data Results */}
            {extractedData && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-green-900/30 to-blue-900/30 rounded-xl p-4 backdrop-blur-xl"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-white font-medium">Extraction Complete</h3>
                  <CheckCircle className="w-5 h-5 text-green-400" />
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Patient Name:</span>
                    <span className="text-white">{extractedData.patient_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Patient ID:</span>
                    <span className="text-white">{extractedData.patient_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Date of Service:</span>
                    <span className="text-white">{extractedData.date_of_service}</span>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-500 transition-colors">
                      View Full Results
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
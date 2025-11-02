import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import fontRoutes from './routes/fontRoutes'
import './database/db' // 初始化数据库

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3001

// 中间件
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5174',
  credentials: true,
}))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// 路由
app.use('/api', fontRoutes)

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

app.listen(PORT, () => {
  console.log(`🚀 Server is running on http://localhost:${PORT}`)
})


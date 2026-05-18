import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { TopBar } from '@/widgets/top-bar'
import AppRouter from './app/router'
import Providers from './app/providers'
import './shared/styles/globals.css'
import { client } from '@/shared/api'
import { useUserStore } from '@/entities/user/model/store'

// Sync client auth with persisted token before first render
const token = useUserStore.getState().token
if (token) {
  client.setConfig({ auth: token })
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Providers>
      <BrowserRouter>
        <TopBar />          {/* minimal top bar — no header, no footer */}
        <AppRouter />
      </BrowserRouter>
    </Providers>
  </React.StrictMode>
)

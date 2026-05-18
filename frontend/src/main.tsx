import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { TopBar } from '@/widgets/top-bar'
import AppRouter from './app/router'
import Providers from './app/providers'
import './shared/styles/globals.css'
import { client } from '@/shared/api'
import { useUserStore } from '@/entities/user/model/store'

// Helper for Cypress e2e: programmatically inject token
if (typeof window !== 'undefined') {
  (window as unknown as Record<string, unknown>).__setAuth = (token: string, user: object) => {
    useUserStore.getState().setToken(token)
    useUserStore.getState().setUser(user as any)
  }
}

// Every request with Bearer security reads the CURRENT token from Zustand.
// No manual re-config needed on login/logout.
client.setConfig({
  auth: () => {
    const token = useUserStore.getState().token
    return token ?? undefined
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Providers>
      <BrowserRouter>
        <TopBar />          {/* minimal top bar — no header, no footer */}
        <AppRouter />
      </BrowserRouter>
    </Providers>
  </React.StrictMode>,
)

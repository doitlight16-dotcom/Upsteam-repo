import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { TenantProvider } from './context/TenantContext'
import { ChatProvider } from './context/ChatContext'

// Extract tenant ID from URL params (e.g. ?tenant=my-org)
const params = new URLSearchParams(window.location.search);
const tenantId = params.get('tenant') || 'default';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <TenantProvider tenantId={tenantId}>
      <ChatProvider tenantId={tenantId}>
        <App />
      </ChatProvider>
    </TenantProvider>
  </StrictMode>,
)

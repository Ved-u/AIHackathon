import ChatWindow from '../components/Chat/ChatWindow';

// ─────────────────────────────────────────────────────────────────────────────
// INTEGRATION GUIDE (uncomment & use when merging into the CMP project)
// ─────────────────────────────────────────────────────────────────────────────
//
// PRE-REQUISITE — Make sure the CMP app has React Router installed.
// If not already installed, run this in the CMP project root:
//
//   npm install react-router-dom
//
// Then in the CMP app's main router file, ensure these imports exist:
//
//   import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
//
// ─────────────────────────────────────────────────────────────────────────────
//
// Step 1 — Import this component inside the CMP app's router file:
//
//   import ContractAnalysis from './modules/contract-analysis/pages/ContractAnalysis';
//
// Step 2 — Add a route inside <Routes> (React Router v6):
//
//   <Routes>
//     {/* ...existing CMP routes... */}
//     <Route path="/contract-analysis" element={<ContractAnalysis />} />
//   </Routes>
//
// Step 3 — Add the menu item in the CMP sidebar (refer ss1 / ss2):
//
//   <NavLink to="/contract-analysis">Contract Analysis</NavLink>
//
// Step 4 (optional) — Pass the logged-in CMP user if the backend needs it:
//
//   <Route path="/contract-analysis" element={<ContractAnalysis user={cmpUser} />} />
//   // ChatWindow can then forward user info in the API request headers/body.
//
// Note: Login is handled by the CMP app. No login needed inside this module.
// ─────────────────────────────────────────────────────────────────────────────

export default function ContractAnalysis() {
  return (
    <div className="ca-layout">
      <div className="ca-body">
        <main className="ca-main">
          <ChatWindow />
        </main>
      </div>
    </div>
  );
}

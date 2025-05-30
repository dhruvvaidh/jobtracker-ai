import React, { useState, createContext, useContext } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import Dashboard from './Dashboard';

interface AuthContextType { token: string; setToken: (t: string) => void; }
const AuthContext = createContext<AuthContextType>({ token: '', setToken: () => {} });
export const useAuth = () => useContext(AuthContext);

const App: React.FC = () => {
  const [token, setToken] = useState('');
  return (
    <AuthContext.Provider value={{ token, setToken }}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={token ? <Dashboard/> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </AuthContext.Provider>
  );
};

const LoginPage: React.FC = () => {
  const { setToken } = useAuth();
  const navigate = useNavigate();

  const handleSuccess = async (res: CredentialResponse) => {
    const idToken = res.credential!;
    // send to backend for verification
    const resp = await axios.post(
      `${process.env.REACT_APP_API_BASE_URL}/auth/google`,
      { token: idToken }
    );
    setToken(resp.data.access_token);
    navigate('/dashboard');
  };

  return (
    <div style={{ display:'flex', justifyContent:'center', marginTop:100 }}>
      <GoogleLogin onSuccess={handleSuccess} onError={() => alert('Login Failed')} />
    </div>
  );
};

export default App;
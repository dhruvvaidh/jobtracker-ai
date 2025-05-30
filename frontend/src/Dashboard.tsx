import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from './App';

interface Counts { Applied:number; Interviewing:number; Offer:number; Rejected:number; }

const Dashboard: React.FC = () => {
  const { token } = useAuth();
  const [counts, setCounts] = useState<Counts>({Applied:0,Interviewing:0,Offer:0,Rejected:0});

  const fetchData = async () => {
    await axios.post(`${process.env.REACT_APP_API_BASE_URL}/refresh`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const { data } = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/applications`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setCounts(data.counts);
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <div style={{ padding:20 }}>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:16 }}>
        {(['Applied','Interviewing','Offer','Rejected'] as const).map(status =>
          <div key={status} style={{ padding:20, border:'1px solid #ccc', borderRadius:8 }}>
            <h3>{status}</h3>
            <p style={{ fontSize:24 }}>{counts[status]}</p>
          </div>
        )}
      </div>
      <button style={{ marginTop:20 }} onClick={fetchData}>Refresh</button>
    </div>
  );
};

export default Dashboard;
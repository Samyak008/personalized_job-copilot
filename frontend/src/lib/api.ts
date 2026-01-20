import axios from 'axios';
import { supabase } from './supabase';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Attach Supabase Session Token
api.interceptors.request.use(async (config) => {
    const { data: { session } } = await supabase.auth.getSession();

    if (session?.access_token) {
        console.log('[API] Attaching Token:', session.access_token.substring(0, 10) + '...');
        config.headers.Authorization = `Bearer ${session.access_token}`;
    } else {
        console.warn('[API] No active session token found!');
    }

    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;

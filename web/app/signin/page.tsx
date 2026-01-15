"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function SigninPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log('Signin Data:', formData);
        // TODO: Connect to backend authentication
        router.push('/');
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-black bg-opacity-90 relative overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob"></div>
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-cyan-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob animation-delay-2000"></div>

            <div className="relative z-10 w-full max-w-md p-8 sm:p-10 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl">
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-bold text-white mb-2">
                        Welcome Back
                    </h1>
                    <p className="text-gray-400">Sign in to continue to your dashboard</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Email Field */}
                    <div className="space-y-2">
                        <label htmlFor="email" className="text-sm font-medium text-gray-300">
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="john@example.com"
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-500 transition-all duration-200"
                            required
                        />
                    </div>

                    {/* Password Field */}
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <label htmlFor="password" className="text-sm font-medium text-gray-300">
                                Password
                            </label>
                            <a href="#" className="text-xs text-blue-500 hover:text-blue-400 transition-colors">
                                Forgot password?
                            </a>
                        </div>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="••••••••"
                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-500 transition-all duration-200"
                            required
                        />
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        className="w-full py-3.5 px-4 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-lg shadow-lg transform transition hover:scale-[1.02] active:scale-[0.98] duration-200"
                    >
                        Sign In
                    </button>
                </form>

                <div className="mt-8 text-center text-sm text-gray-400">
                    Don't have an account?{' '}
                    <Link href="/signup" className="text-blue-500 hover:text-blue-400 font-medium transition-colors">
                        Sign Up
                    </Link>
                </div>
            </div>
        </div>
    );
}

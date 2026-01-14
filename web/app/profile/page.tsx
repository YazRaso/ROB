"use client";

import Link from "next/link";

export default function ProfilePage() {
    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <header className="space-y-2">
                <h2 className="text-3xl font-extrabold tracking-tight text-white">Profile & Settings</h2>
                <p className="text-zinc-400">
                    Manage your account preferences and API keys.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Profile Card */}
                <div className="md:col-span-1 space-y-6">
                    <div className="glass-card p-6 rounded-3xl flex flex-col items-center text-center">
                        <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 mb-4 shadow-xl shadow-indigo-500/20" />
                        <h3 className="text-xl font-bold text-white">User</h3>
                        <p className="text-sm text-zinc-400 mb-6">user@example.com</p>
                        <div className="w-full space-y-2">
                            <button className="btn-secondary w-full">Edit Profile</button>
                            <button className="btn-secondary w-full text-red-400 hover:text-red-300 hover:bg-red-500/10 border-red-500/20">Sign Out</button>
                        </div>
                    </div>

                    {/* Plan Status */}
                    <div className="glass-card p-6 rounded-3xl">
                        <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest mb-4">Plan Usage</h4>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-zinc-300">API Calls</span>
                                    <span className="text-zinc-500">850 / 1000</span>
                                </div>
                                <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                                    <div className="h-full w-[85%] bg-indigo-500 rounded-full" />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-zinc-300">Storage</span>
                                    <span className="text-zinc-500">2.1 GB / 5 GB</span>
                                </div>
                                <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                                    <div className="h-full w-[42%] bg-purple-500 rounded-full" />
                                </div>
                            </div>
                        </div>
                        <div className="mt-6">
                            <button className="btn-primary w-full text-sm">Upgrade Plan</button>
                        </div>
                    </div>
                </div>

                {/* Settings Form */}
                <div className="md:col-span-2 space-y-6">
                    <div className="glass-card p-8 rounded-3xl">
                        <h3 className="text-lg font-bold mb-6">Account Settings</h3>
                        <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-zinc-400">First Name</label>
                                    <input type="text" defaultValue="Backboard" className="w-full bg-zinc-800/50 border border-zinc-700 rounded-xl px-4 py-2.5 text-zinc-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-zinc-400">Last Name</label>
                                    <input type="text" defaultValue="User" className="w-full bg-zinc-800/50 border border-zinc-700 rounded-xl px-4 py-2.5 text-zinc-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-400">Email Address</label>
                                <input type="email" defaultValue="user@backboard.io" className="w-full bg-zinc-800/50 border border-zinc-700 rounded-xl px-4 py-2.5 text-zinc-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all" />
                            </div>
                        </div>
                        <div className="mt-8 flex justify-end">
                            <button className="btn-primary">Save Changes</button>
                        </div>
                    </div>

                    <div className="glass-card p-8 rounded-3xl">
                        <h3 className="text-lg font-bold mb-6">Preferences</h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-4 bg-zinc-800/30 rounded-xl border border-zinc-700/30">
                                <div className="flex items-center gap-3">
                                    <span className="material-symbols-outlined text-zinc-400">dark_mode</span>
                                    <div>
                                        <h4 className="font-medium text-zinc-200">Dark Mode</h4>
                                        <p className="text-xs text-zinc-500">Use system preference</p>
                                    </div>
                                </div>
                                <div className="w-10 h-6 bg-indigo-600 rounded-full relative cursor-pointer">
                                    <div className="absolute top-1 right-1 w-4 h-4 bg-white rounded-full shadow-sm" />
                                </div>
                            </div>
                            <div className="flex items-center justify-between p-4 bg-zinc-800/30 rounded-xl border border-zinc-700/30">
                                <div className="flex items-center gap-3">
                                    <span className="material-symbols-outlined text-zinc-400">notifications</span>
                                    <div>
                                        <h4 className="font-medium text-zinc-200">Notifications</h4>
                                        <p className="text-xs text-zinc-500">Receive email updates</p>
                                    </div>
                                </div>
                                <div className="w-10 h-6 bg-zinc-700 rounded-full relative cursor-pointer">
                                    <div className="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-sm" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

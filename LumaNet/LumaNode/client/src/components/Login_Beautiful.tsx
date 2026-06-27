import React, { useState, useEffect } from 'react';
import { api } from '../api/lumanetApi';

interface LoginProps {
  onLogin: (user: any) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userType, setUserType] = useState('student');
  const [isDark, setIsDark] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    // Ensure we start in light mode
    document.documentElement.classList.remove('dark');
  }, []);

  const toggleTheme = () => {
    const newDarkMode = !isDark;
    setIsDark(newDarkMode);
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.login({ username, password });
      
      // Store token and user data
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      onLogin(response.user);
    } catch (error: any) {
      console.error('Login failed:', error);
      setError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen flex ${isDark ? 'dark' : ''}`}>
      {/* Left Side - Blue Gradient (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-400 to-blue-600 dark:from-blue-600 dark:to-blue-800 p-8 lg:p-12 flex-col justify-between text-white relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-300/20 to-transparent"></div>
        
        {/* Header */}
        <div className="relative z-10 mt-8 lg:mt-16">
          <h1 className="text-3xl lg:text-5xl font-bold mb-3" style={{fontFamily: 'Bricolage Grotesque, sans-serif'}}>LumaNet</h1>
          <p className="text-blue-100 text-base lg:text-lg leading-relaxed">An innovative low-cost mesh network solution to uplift regions with little to no internet stability</p>
        </div>

        {/* Features */}
        <div className="relative z-10 space-y-6 lg:space-y-8">
          <div className="flex items-start space-x-3 lg:space-x-4">
            <div className="w-10 h-10 lg:w-12 lg:h-12 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm flex-shrink-0">
              <svg className="w-5 h-5 lg:w-6 lg:h-6" fill="currentColor" viewBox="0 0 20 20">
                <path d="M12 14l9-5-9-5-9 5 9 5z"/>
                <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/>
              </svg>
            </div>
            <div className="min-w-0">
              <h3 className="text-lg lg:text-xl font-semibold mb-1 lg:mb-2">Interactive Learning</h3>
              <p className="text-blue-100 text-sm lg:text-base">Access courses, materials, and resources offline with seamless synchronization</p>
            </div>
          </div>

          <div className="flex items-start space-x-3 lg:space-x-4">
            <div className="w-10 h-10 lg:w-12 lg:h-12 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm flex-shrink-0">
              <svg className="w-5 h-5 lg:w-6 lg:h-6" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
              </svg>
            </div>
            <div className="min-w-0">
              <h3 className="text-lg lg:text-xl font-semibold mb-1 lg:mb-2">Collaborative Environment</h3>
              <p className="text-blue-100 text-sm lg:text-base">Connect with classmates and instructors in a secure learning network</p>
            </div>
          </div>

          <div className="flex items-start space-x-3 lg:space-x-4">
            <div className="w-10 h-10 lg:w-12 lg:h-12 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm flex-shrink-0">
              <svg className="w-5 h-5 lg:w-6 lg:h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
              </svg>
            </div>
            <div className="min-w-0">
              <h3 className="text-lg lg:text-xl font-semibold mb-1 lg:mb-2">Progress Tracking</h3>
              <p className="text-blue-100 text-sm lg:text-base">Monitor your learning journey with detailed analytics and achievements</p>
            </div>
          </div>
          
          {/* Separator line */}
          <div className="border-t border-white/20 pt-4"></div>
        </div>

        {/* Footer */}
        <div className="relative z-10 flex justify-between items-center">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm">Status: Available</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 p-4 lg:p-8 flex flex-col justify-center relative">
        {/* Theme Toggle */}
        <div className="absolute top-4 right-4 lg:top-6 lg:right-6">
          <button
            onClick={toggleTheme}
            className="p-2 lg:p-3 rounded-xl bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-300"
            aria-label="Toggle theme"
          >
            {isDark ? (
              <svg className="w-4 h-4 lg:w-5 lg:h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-4 h-4 lg:w-5 lg:h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
        </div>

        <div className="max-w-md mx-auto w-full">
          {/* Logo and Branding */}
          <div className="text-center mb-6 lg:mb-10">
            <div className="w-16 h-16 lg:w-20 lg:h-20 mx-auto mb-4 lg:mb-6">
              <img src="/logo.png" alt="LumaNet Logo" className="w-full h-full object-contain" />
            </div>
            <h2 className="text-base lg:text-lg font-medium text-gray-600 dark:text-gray-400 mb-1">Sign In</h2>
            <p className="text-sm text-gray-500 dark:text-gray-500">Access your dashboard</p>
          </div>

          {/* User Type Selection */}
          <div className="mb-6 lg:mb-8">
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Choose Portal</label>
            <div className="flex space-x-2 lg:space-x-3">
              <button
                type="button"
                onClick={() => setUserType('student')}
                className={`flex-1 p-2 lg:p-3 rounded-xl text-xs lg:text-sm font-medium transition-all duration-200 ${
                  userType === 'student'
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                Student Portal
              </button>
              
              <button
                type="button"
                onClick={() => setUserType('admin')}
                className={`flex-1 p-2 lg:p-3 rounded-xl text-xs lg:text-sm font-medium transition-all duration-200 ${
                  userType === 'admin'
                    ? 'bg-yellow-500 text-white shadow-lg'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                Admin Portal
              </button>
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-4 lg:space-y-6">
            <div className="space-y-3 lg:space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-3 py-2 lg:px-4 lg:py-3 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all duration-200 shadow-sm hover:shadow-md text-sm lg:text-base"
                  placeholder="Enter your username"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3 py-2 lg:px-4 lg:py-3 pr-10 lg:pr-12 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all duration-200 shadow-sm hover:shadow-md text-sm lg:text-base"
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    {showPassword ? (
                      <svg className="w-4 h-4 lg:w-5 lg:h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                        <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4 lg:w-5 lg:h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                        <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-3 py-2 lg:px-4 lg:py-3 rounded-xl text-xs lg:text-sm font-medium">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full font-semibold py-3 lg:py-4 px-4 lg:px-6 rounded-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-xl text-sm lg:text-base ${
                userType === 'admin'
                  ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-white shadow-yellow-500/25'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-blue-500/25'
              }`}
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-4 w-4 lg:h-5 lg:w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </div>
              ) : (
                `Access ${userType === 'admin' ? 'Admin' : 'Student'} Portal`
              )}
            </button>
          </form>

          {/* Demo Info */}
          <div className="mt-6 lg:mt-8 p-3 lg:p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-center mb-2">
              <svg className="w-3 h-3 lg:w-4 lg:h-4 text-blue-600 dark:text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
              </svg>
              <span className="text-xs lg:text-sm font-semibold text-blue-800 dark:text-blue-300">Demo Credentials</span>
            </div>
            <div className="text-xs text-blue-700 dark:text-blue-400 text-center space-y-1">
              <div><span className="font-medium">Student:</span> student / student123</div>
              <div><span className="font-medium">Admin:</span> admin / admin123</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

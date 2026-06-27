import React from 'react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

const Logo: React.FC<LogoProps> = ({ size = 'md', showText = true }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl'
  };

  return (
    <div className="flex items-center space-x-3">
      <div className={`${sizeClasses[size]} relative`}>
        <svg
          viewBox="0 0 100 100"
          className="w-full h-full"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Outer ring */}
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="url(#gradient1)"
            strokeWidth="4"
            fill="none"
            className="animate-pulse"
          />
          
          {/* Inner network nodes */}
          <circle cx="50" cy="25" r="6" fill="url(#gradient2)" />
          <circle cx="75" cy="50" r="6" fill="url(#gradient2)" />
          <circle cx="50" cy="75" r="6" fill="url(#gradient2)" />
          <circle cx="25" cy="50" r="6" fill="url(#gradient2)" />
          <circle cx="50" cy="50" r="8" fill="url(#gradient3)" />
          
          {/* Connection lines */}
          <line x1="50" y1="31" x2="50" y2="42" stroke="url(#gradient1)" strokeWidth="2" />
          <line x1="69" y1="50" x2="58" y2="50" stroke="url(#gradient1)" strokeWidth="2" />
          <line x1="50" y1="69" x2="50" y2="58" stroke="url(#gradient1)" strokeWidth="2" />
          <line x1="31" y1="50" x2="42" y2="50" stroke="url(#gradient1)" strokeWidth="2" />
          
          {/* Gradients */}
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#1d4ed8" />
            </linearGradient>
            <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#60a5fa" />
              <stop offset="100%" stopColor="#2563eb" />
            </linearGradient>
            <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#93c5fd" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      
      {showText && (
        <span className={`font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent ${textSizeClasses[size]}`}>
          LumaNet
        </span>
      )}
    </div>
  );
};

export default Logo;

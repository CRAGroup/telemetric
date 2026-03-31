import { Truck } from "lucide-react";
import { useState } from "react";

// Placeholder for admin settings - needs API endpoint
const useAdminSettings = () => {
  return {
    settings: {
      company_name: "Fleet Manager",
      company_logo_url: null
    },
    loading: false,
    error: null
  };
};

interface CompanyLogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
}

export function CompanyLogo({ size = "md", showText = true, className = "" }: CompanyLogoProps) {
  const { settings, loading, error } = useAdminSettings();
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const sizeClasses = {
    sm: "w-6 h-6",
    md: "w-8 h-8", 
    lg: "w-10 h-10"
  };

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6"
  };

  const textSizes = {
    sm: "text-sm",
    md: "text-lg",
    lg: "text-xl"
  };

  // Use fallback values immediately to avoid loading delay
  const companyName = settings?.company_name || "Fleet Manager";
  const logoUrl = settings?.company_logo_url;
  
  // Show logo immediately if we have URL, otherwise show truck icon
  const shouldShowImage = logoUrl && !imageError;
  const shouldShowIcon = !logoUrl || imageError || !imageLoaded;

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <div className={`${sizeClasses[size]} rounded-lg bg-primary flex items-center justify-center flex-shrink-0 overflow-hidden relative`}>
        {/* Show image if URL exists */}
        {shouldShowImage && (
          <img 
            src={logoUrl} 
            alt={`${companyName} Logo`}
            className={`w-full h-full object-cover transition-opacity duration-200 ${
              imageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={() => {
              setImageLoaded(true);
              setImageError(false);
            }}
            onError={() => {
              setImageError(true);
              setImageLoaded(false);
            }}
          />
        )}
        
        {/* Show truck icon as fallback or while loading */}
        {shouldShowIcon && (
          <Truck 
            className={`${iconSizes[size]} text-primary-foreground transition-opacity duration-200 ${
              shouldShowImage && !imageLoaded ? 'opacity-100' : shouldShowImage ? 'opacity-0 absolute' : 'opacity-100'
            }`} 
          />
        )}
        
        {/* Loading indicator only for initial load */}
        {loading && !settings && (
          <div className="absolute inset-0 bg-primary animate-pulse" />
        )}
      </div>
      
      {showText && (
        <div className="hidden sm:block">
          {loading && !settings ? (
            <div className="h-4 w-24 bg-muted animate-pulse rounded" />
          ) : (
            <h2 className={`${textSizes[size]} font-bold`}>{companyName}</h2>
          )}
        </div>
      )}
    </div>
  );
}
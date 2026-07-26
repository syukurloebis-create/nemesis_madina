/**
 * Authentication Hook
 * Convenience hook for auth operations
 */
import { useAuth as useAuthContext } from '../context/AuthContext';

export const useAuth = () => {
  return useAuthContext();
};

// For backward compatibility
export default useAuth;
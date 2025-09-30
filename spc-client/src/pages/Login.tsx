import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { gitlabApi } from '@/lib/api';
import { GitBranch } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { toast } = useToast();
  const { setCredentials, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = React.useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/create-project');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    // SECURITY: Parse from URL hash (fragment) instead of query parameters
    // This prevents token leakage through Referer headers and browser history
    const parseHashParams = () => {
      const hash = window.location.hash.substring(1); // Remove '#'
      const params = new URLSearchParams(hash);
      return {
        success: params.get('success'),
        error: params.get('error'),
        access_token: params.get('access_token'),
        token_type: params.get('token_type'),
        expires_in: params.get('expires_in')
      };
    };

    // Try hash first (new secure method), fallback to query params for backwards compatibility
    const hashParams = parseHashParams();
    const hasHashParams = hashParams.access_token || hashParams.error;

    const success = hasHashParams ? hashParams.success : searchParams.get('success');
    const error = hasHashParams ? hashParams.error : searchParams.get('error');
    const access_token = hasHashParams ? hashParams.access_token : searchParams.get('access_token');
    const token_type = hasHashParams ? hashParams.token_type : searchParams.get('token_type');
    const expires_in = hasHashParams ? hashParams.expires_in : searchParams.get('expires_in');

    // Basic input sanitization for OAuth parameters
    const sanitizeParam = (param: string | null): string | null => {
      if (!param) return null;
      // Remove potentially dangerous characters but preserve valid OAuth tokens/parameters
      return param.replace(/[<>\"'\\&]/g, '').trim();
    };

    const sanitizedError = sanitizeParam(error);
    const sanitizedAccessToken = sanitizeParam(access_token);
    const sanitizedTokenType = sanitizeParam(token_type);

    // Clear the hash after parsing to avoid token exposure
    if (hasHashParams && sanitizedAccessToken) {
      window.history.replaceState(null, '', window.location.pathname);
    }

    if (success && sanitizedAccessToken && sanitizedTokenType) {
      // Additional validation for token format
      if (sanitizedAccessToken.length < 10 || sanitizedAccessToken.length > 500) {
        toast({
          title: 'Authentication failed',
          description: 'Invalid token format received',
          variant: 'destructive',
        });
        return;
      }

      // Handle successful OAuth callback
      const credentials = {
        access_token: sanitizedAccessToken,
        token_type: sanitizedTokenType,
        expires_in: expires_in ? parseInt(expires_in) : undefined,
      };
      setCredentials(credentials);
      toast({
        title: 'Authentication successful',
        description: 'Welcome to Solid Project Creator',
      });
      navigate('/create-project');
    } else if (sanitizedError) {
      // Handle OAuth errors
      const allowedErrors = ['missing_code', 'token_exchange_failed', 'gitlab_unreachable'];
      const errorMessages = {
        missing_code: 'Authorization code was missing',
        token_exchange_failed: 'Failed to exchange token with GitLab',
        gitlab_unreachable: 'Unable to contact GitLab servers',
      };
      
      // Only show error if it's in our allowed list
      if (allowedErrors.includes(sanitizedError)) {
        toast({
          title: 'Authentication failed',
          description: errorMessages[sanitizedError as keyof typeof errorMessages],
          variant: 'destructive',
        });
      } else {
        toast({
          title: 'Authentication failed',
          description: 'An unknown error occurred',
          variant: 'destructive',
        });
      }
    }
  }, [searchParams, setCredentials, toast, navigate]);


  const handleGitLabLogin = async () => {
    setIsLoading(true);
    try {
      const { login_url } = await gitlabApi.getLoginUrl();
      window.location.href = login_url;
    } catch (error: unknown) {
      toast({
        title: 'Login Error',
        description: 'Failed to initiate GitLab login. Please try again.',
        variant: 'destructive',
      });
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center space-y-4">
              <img 
                src="/logo.svg" 
                alt="Solid Project Creator" 
                className="h-12 w-12 animate-pulse"
              />
              <p>Authenticating...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <img 
              src="/logo.svg" 
              alt="Solid Project Creator" 
              className="h-16 w-16"
            />
          </div>
          <CardTitle className="text-2xl">Solid Project Creator</CardTitle>
          <CardDescription>
            Sign in with your GitLab account to create and configure repositories with automated templates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={handleGitLabLogin} 
            className="w-full" 
            disabled={isLoading}
          >
            Sign In with GitLab
          </Button>
          <div className="mt-4 text-center text-sm text-muted-foreground">
            <p>
              By signing in, you authorize this application to access your GitLab account 
              and create repositories on your behalf.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
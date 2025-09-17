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
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    const access_token = searchParams.get('access_token');
    const token_type = searchParams.get('token_type');
    const expires_in = searchParams.get('expires_in');

    if (success && access_token && token_type) {
      // Handle successful OAuth callback
      const credentials = {
        access_token,
        token_type,
        expires_in: expires_in ? parseInt(expires_in) : undefined,
      };
      setCredentials(credentials);
      toast({
        title: 'Authentication successful',
        description: 'Welcome to Solid Project Creator',
      });
      navigate('/create-project');
    } else if (error) {
      // Handle OAuth errors
      const errorMessages = {
        missing_code: 'Authorization code was missing',
        token_exchange_failed: 'Failed to exchange token with GitLab',
        gitlab_unreachable: 'Unable to contact GitLab servers',
      };
      toast({
        title: 'Authentication failed',
        description: errorMessages[error as keyof typeof errorMessages] || 'An unknown error occurred',
        variant: 'destructive',
      });
    }
  }, [searchParams, setCredentials, toast, navigate]);


  const handleGitLabLogin = async () => {
    setIsLoading(true);
    try {
      const { login_url } = await gitlabApi.getLoginUrl();
      window.location.href = login_url;
    } catch (error) {
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
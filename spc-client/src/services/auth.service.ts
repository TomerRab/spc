import { gitlabApi } from '@/lib/api';

export class AuthService {
  static async getLoginUrl(): Promise<{ login_url: string }> {
    return gitlabApi.getLoginUrl();
  }
}

export const authService = new AuthService();
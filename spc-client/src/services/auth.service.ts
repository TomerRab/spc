import { gitlabApi } from '@/lib/api';
import { API_ENDPOINTS } from '@/constants';

export class AuthService {
  static async getLoginUrl(): Promise<{ login_url: string }> {
    return gitlabApi.get(API_ENDPOINTS.AUTH.LOGIN);
  }
}

export const authService = new AuthService();
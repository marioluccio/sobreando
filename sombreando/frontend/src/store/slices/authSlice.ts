import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authService } from '@/services/authService';
import { secureStorage } from '@/utils/secureStorage';
import { 
  AuthState, 
  LoginCredentials, 
  RegisterData, 
  User, 
  AuthTokens,
  ApiError 
} from '@/types';

// Initial state
const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  requires2FA: false,
};

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await authService.login(credentials);
      
      // Store tokens securely
      await secureStorage.setTokens({
        access: response.access,
        refresh: response.refresh,
      });
      
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao fazer login';
      const requires2FA = error.response?.data?.requires_2fa || false;
      
      return rejectWithValue({
        message: errorMessage,
        requires2FA,
      });
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async (userData: RegisterData, { rejectWithValue }) => {
    try {
      const response = await authService.register(userData);
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao registrar usuário';
      return rejectWithValue({ message: errorMessage });
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logoutUser',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState };
      const refreshToken = state.auth.tokens?.refresh;
      
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
      
      // Clear stored tokens
      await secureStorage.clearTokens();
      
      return null;
    } catch (error: any) {
      // Even if logout fails on server, clear local tokens
      await secureStorage.clearTokens();
      return null;
    }
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState };
      const refreshTokenValue = state.auth.tokens?.refresh;
      
      if (!refreshTokenValue) {
        throw new Error('No refresh token available');
      }
      
      const response = await authService.refreshToken(refreshTokenValue);
      
      // Update stored tokens
      const newTokens = {
        access: response.access,
        refresh: refreshTokenValue, // Keep the same refresh token
      };
      
      await secureStorage.setTokens(newTokens);
      
      return newTokens;
    } catch (error: any) {
      // If refresh fails, logout user
      await secureStorage.clearTokens();
      return rejectWithValue({ message: 'Sessão expirada' });
    }
  }
);

export const loadStoredAuth = createAsyncThunk(
  'auth/loadStoredAuth',
  async (_, { rejectWithValue }) => {
    try {
      const tokens = await secureStorage.getTokens();
      
      if (!tokens.access || !tokens.refresh) {
        await secureStorage.clearTokens();
        return null;
      }
      
      // Validate tokens by getting current user
      const user = await authService.getCurrentUser();
      
      return {
        user,
        tokens,
      };
    } catch (error: any) {
      // If validation fails, clear tokens
      await secureStorage.clearTokens();
      return null;
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData: Partial<User>, { rejectWithValue }) => {
    try {
      const response = await authService.updateProfile(profileData);
      return response;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao atualizar perfil';
      return rejectWithValue({ message: errorMessage });
    }
  }
);

export const verifyEmail = createAsyncThunk(
  'auth/verifyEmail',
  async (token: string, { rejectWithValue }) => {
    try {
      await authService.verifyEmail(token);
      return null;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao verificar email';
      return rejectWithValue({ message: errorMessage });
    }
  }
);

export const toggle2FA = createAsyncThunk(
  'auth/toggle2FA',
  async (
    { enable, verificationCode }: { enable: boolean; verificationCode?: string },
    { rejectWithValue }
  ) => {
    try {
      await authService.toggle2FA(enable, verificationCode);
      return enable;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao alterar 2FA';
      const requiresVerification = error.response?.data?.requires_verification || false;
      
      return rejectWithValue({
        message: errorMessage,
        requiresVerification,
      });
    }
  }
);

// Auth slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearRequires2FA: (state) => {
      state.requires2FA = false;
    },
    setTokens: (state, action: PayloadAction<AuthTokens>) => {
      state.tokens = action.payload;
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    resetAuth: () => initialState,
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
        state.requires2FA = false;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.tokens = {
          access: action.payload.access,
          refresh: action.payload.refresh,
        };
        state.error = null;
        state.requires2FA = false;
      })
      .addCase(loginUser.rejected, (state, action: any) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.tokens = null;
        state.error = action.payload?.message || 'Erro ao fazer login';
        state.requires2FA = action.payload?.requires2FA || false;
      });

    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action: any) => {
        state.isLoading = false;
        state.error = action.payload?.message || 'Erro ao registrar usuário';
      });

    // Logout
    builder
      .addCase(logoutUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        return initialState;
      })
      .addCase(logoutUser.rejected, (state) => {
        return initialState;
      });

    // Refresh token
    builder
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.tokens = action.payload;
      })
      .addCase(refreshToken.rejected, (state) => {
        return initialState;
      });

    // Load stored auth
    builder
      .addCase(loadStoredAuth.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(loadStoredAuth.fulfilled, (state, action) => {
        state.isLoading = false;
        if (action.payload) {
          state.isAuthenticated = true;
          state.user = action.payload.user;
          state.tokens = action.payload.tokens;
        }
      })
      .addCase(loadStoredAuth.rejected, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.tokens = null;
      });

    // Update profile
    builder
      .addCase(updateProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(updateProfile.rejected, (state, action: any) => {
        state.isLoading = false;
        state.error = action.payload?.message || 'Erro ao atualizar perfil';
      });

    // Verify email
    builder
      .addCase(verifyEmail.fulfilled, (state) => {
        if (state.user) {
          state.user.is_verified = true;
        }
      })
      .addCase(verifyEmail.rejected, (state, action: any) => {
        state.error = action.payload?.message || 'Erro ao verificar email';
      });

    // Toggle 2FA
    builder
      .addCase(toggle2FA.fulfilled, (state, action) => {
        if (state.user) {
          state.user.is_2fa_enabled = action.payload;
        }
      })
      .addCase(toggle2FA.rejected, (state, action: any) => {
        state.error = action.payload?.message || 'Erro ao alterar 2FA';
      });
  },
});

// Export actions
export const { 
  clearError, 
  clearRequires2FA, 
  setTokens, 
  updateUser, 
  resetAuth 
} = authSlice.actions;

// Export selectors
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectUser = (state: { auth: AuthState }) => state.auth.user;
export const selectIsAuthenticated = (state: { auth: AuthState }) => state.auth.isAuthenticated;
export const selectAuthLoading = (state: { auth: AuthState }) => state.auth.isLoading;
export const selectAuthError = (state: { auth: AuthState }) => state.auth.error;
export const selectRequires2FA = (state: { auth: AuthState }) => state.auth.requires2FA;

export default authSlice.reducer;


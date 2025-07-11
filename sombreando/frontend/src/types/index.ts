// User types
export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  avatar?: string;
  company_name: string;
  is_verified: boolean;
  is_2fa_enabled: boolean;
  subscription_plan: SubscriptionPlan;
  is_subscription_active: boolean;
  created_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  bio: string;
  location: string;
  website: string;
  birth_date?: string;
  language: string;
  timezone: string;
  email_notifications: boolean;
  push_notifications: boolean;
  marketing_emails: boolean;
  profile_visibility: 'public' | 'private' | 'friends';
}

export type SubscriptionPlan = 'free' | 'basic' | 'premium' | 'enterprise';

// Authentication types
export interface LoginCredentials {
  email: string;
  password: string;
  verification_code?: string;
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone?: string;
  company_name?: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  requires2FA: boolean;
}

// API Response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success?: boolean;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status?: number;
}

// Navigation types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  Onboarding: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
  EmailVerification: { email: string };
  TwoFactorAuth: { email: string };
};

export type MainTabParamList = {
  Home: undefined;
  Maps: undefined;
  Payments: undefined;
  Profile: undefined;
};

export type ProfileStackParamList = {
  ProfileMain: undefined;
  EditProfile: undefined;
  Settings: undefined;
  Security: undefined;
  Subscription: undefined;
  Help: undefined;
};

// Map types
export interface MapLocation {
  latitude: number;
  longitude: number;
  latitudeDelta?: number;
  longitudeDelta?: number;
}

export interface MapMarker {
  id: string;
  coordinate: MapLocation;
  title: string;
  description?: string;
  type?: 'user' | 'poi' | 'service';
}

export interface MapState {
  currentLocation: MapLocation | null;
  markers: MapMarker[];
  isLoading: boolean;
  error: string | null;
  selectedMarker: MapMarker | null;
}

// Payment types
export interface PaymentMethod {
  id: string;
  type: 'credit_card' | 'debit_card' | 'pix' | 'boleto';
  last_four?: string;
  brand?: string;
  is_default: boolean;
  created_at: string;
}

export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'succeeded' | 'failed' | 'canceled';
  payment_method?: PaymentMethod;
  created_at: string;
}

export interface Subscription {
  id: string;
  plan: SubscriptionPlan;
  status: 'active' | 'canceled' | 'past_due' | 'unpaid';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  payment_method?: PaymentMethod;
}

export interface PaymentState {
  paymentMethods: PaymentMethod[];
  subscription: Subscription | null;
  paymentIntents: PaymentIntent[];
  isLoading: boolean;
  error: string | null;
}

// App state types
export interface AppState {
  isOnboardingCompleted: boolean;
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: {
    push: boolean;
    email: boolean;
    marketing: boolean;
  };
  isNetworkConnected: boolean;
}

// Form types
export interface FormField {
  value: string;
  error?: string;
  touched: boolean;
}

export interface LoginForm {
  email: FormField;
  password: FormField;
  verificationCode?: FormField;
}

export interface RegisterForm {
  email: FormField;
  username: FormField;
  firstName: FormField;
  lastName: FormField;
  phone: FormField;
  companyName: FormField;
  password: FormField;
  passwordConfirm: FormField;
}

// Component props types
export interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
}

export interface InputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  autoComplete?: string;
  disabled?: boolean;
  multiline?: boolean;
  numberOfLines?: number;
}

export interface ModalProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  animationType?: 'slide' | 'fade' | 'none';
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Redux types
export interface RootState {
  auth: AuthState;
  app: AppState;
  map: MapState;
  payment: PaymentState;
}

export type AppDispatch = any; // Will be properly typed in store setup

// Error types
export interface ValidationError {
  field: string;
  message: string;
}

export interface NetworkError {
  message: string;
  status?: number;
  isNetworkError: boolean;
}

// Feature flags
export interface FeatureFlags {
  enableMaps: boolean;
  enablePayments: boolean;
  enableNotifications: boolean;
  enableAnalytics: boolean;
  enableBetaFeatures: boolean;
}

// Analytics types
export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  timestamp?: Date;
}

export interface UserStats {
  login_attempts_today: number;
  total_login_attempts: number;
  account_age_days: number;
  is_verified: boolean;
  is_2fa_enabled: boolean;
  subscription_plan: SubscriptionPlan;
  is_subscription_active: boolean;
}


import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { combineReducers } from '@reduxjs/toolkit';

import authSlice from './slices/authSlice';
import appSlice from './slices/appSlice';
import mapSlice from './slices/mapSlice';
import paymentSlice from './slices/paymentSlice';

// Persist config
const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'app'], // Only persist auth and app state
  blacklist: ['map', 'payment'], // Don't persist map and payment state
};

// Auth persist config (more specific)
const authPersistConfig = {
  key: 'auth',
  storage: AsyncStorage,
  whitelist: ['tokens', 'user'], // Only persist tokens and user
  blacklist: ['isLoading', 'error', 'requires2FA'], // Don't persist temporary state
};

// App persist config
const appPersistConfig = {
  key: 'app',
  storage: AsyncStorage,
  whitelist: ['isOnboardingCompleted', 'theme', 'language', 'notifications'],
  blacklist: ['isNetworkConnected'], // Don't persist network state
};

// Root reducer
const rootReducer = combineReducers({
  auth: persistReducer(authPersistConfig, authSlice),
  app: persistReducer(appPersistConfig, appSlice),
  map: mapSlice,
  payment: paymentSlice,
});

// Persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [
          'persist/PERSIST',
          'persist/REHYDRATE',
          'persist/PAUSE',
          'persist/PURGE',
          'persist/REGISTER',
          'persist/FLUSH',
        ],
        ignoredActionsPaths: ['meta.arg', 'payload.timestamp'],
        ignoredPaths: ['items.dates'],
      },
      immutableCheck: {
        ignoredPaths: ['items.dates'],
      },
    }),
  devTools: __DEV__,
});

// Persistor
export const persistor = persistStore(store);

// Types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Reset store (for logout)
export const resetStore = () => {
  persistor.purge();
  store.dispatch({ type: 'RESET_STORE' });
};

export default store;


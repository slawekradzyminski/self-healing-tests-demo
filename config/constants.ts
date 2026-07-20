export const APP_BASE_URL = process.env.APP_BASE_URL ?? 'http://localhost:8081';
export const ADMIN_USER = {
  username: process.env.ADMIN_USERNAME ?? '',
  password: process.env.ADMIN_PASSWORD ?? '',
  displayName: process.env.ADMIN_DISPLAY_NAME ?? '',
  firstName: process.env.ADMIN_FIRST_NAME ?? '',
  email: process.env.ADMIN_EMAIL ?? ''
};

export const ADMIN_PASSWORD = ADMIN_USER.password;

// token存放到cookie
import Cookies from "js-cookie";
const TokenKey = "vite-vue3-ts-token";  // 设置本项目token名称
const RefreshTokenKey = "vite-vue3-ts-refresh-token"; // 刷新token名称

export const getToken = () => {
  return Cookies.get(TokenKey);
}

export const setToken = (token: string, cookieExpires?: number) => {
  return Cookies.set(TokenKey, token, { expires: cookieExpires || 1 });
}

export const removeToken = () => {
  return Cookies.remove(TokenKey);
}

// 刷新token相关
export const getRefreshToken = () => {
  return Cookies.get(RefreshTokenKey);
}

export const setRefreshToken = (token: string, cookieExpires?: number) => {
  return Cookies.set(RefreshTokenKey, token, { expires: cookieExpires || 7 });
}

export const removeRefreshToken = () => {
  return Cookies.remove(RefreshTokenKey);
}

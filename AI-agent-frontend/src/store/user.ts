import { defineStore } from 'pinia'
import { getToken } from '@/utils/auth'

interface ISystemMenu {
  children: Array<ISystemMenuChildren>,
  component: object,
  meta: IMeta,
  path: string,
}

interface ISystemMenuChildren {
  name: string,
  component: object,
  meta: IMeta,
  path: string,
}

interface IMeta {
  title?: string,
  icon?: string,
  iconActive?: string,
  role?: Array<string>,
  hidden?: boolean,
}

export const userStore = defineStore("user", {
  state: () => {
    return {
      token: getToken(),
      userName: '',
      avatar: '',
      role: '',
      systemMenuList: [] as ISystemMenu[],
    }
  },
  getters: {},
  actions: {
    setToken(token: string) {
      this.token = token
    },
    setUserName(userName: string) {
      this.userName = userName
    },
    setAvatar(avatar: string) {
      this.avatar = avatar
    },
    setRole(role: string) {
      this.role = role
    },
  },
  // pinia数据持久化
  persist: {
    key: 'user_info',
    storage: localStorage,
    paths: ['userName', 'avatar', 'role']
  }
})

export interface ILoginParams {
  userName: string
  password: string
}
export interface ILoginApi {
  login: (params: ILoginParams) => Promise<any>
}
